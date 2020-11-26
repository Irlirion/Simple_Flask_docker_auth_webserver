import json
import uuid


class Datastore(object):
    def __init__(self, db):
        self.db = db

    def commit(self):
        pass

    def put(self, model):
        raise NotImplementedError

    def delete(self, model):
        raise NotImplementedError


class SQLAlchemyDatastore(Datastore):
    def commit(self):
        self.db.session.commit()

    def put(self, model):
        self.db.session.add(model)
        return model

    def delete(self, model):
        self.db.session.delete(model)


class UserDatastore(object):
    """Abstracted user datastore.

    :param user_model: A user model class definition

    .. important::
        For mutating operations, the user will be added to the
        datastore (by calling self.put(<object>). If the datastore is session based
        (such as for SQLAlchemyDatastore) it is up to caller to actually
        commit the transaction by calling datastore.commit().
    """

    def __init__(self, user_model):
        self.user_model = user_model

    def _prepare_role_modify_args(self, user):
        if isinstance(user, str):
            user = self.find_user(email=user)
        return user

    def _prepare_create_user_args(self, **kwargs):
        kwargs.setdefault("active", True)
        if hasattr(self.user_model, "fs_uniquifier"):
            kwargs.setdefault("fs_uniquifier", uuid.uuid4().hex)
        return kwargs

    def _is_numeric(self, value):
        try:
            int(value)
        except (TypeError, ValueError):
            return False
        return True

    def _is_uuid(self, value):
        return isinstance(value, uuid.UUID)

    def get_user(self, id_or_email):
        """Returns a user matching the specified ID or email address."""
        raise NotImplementedError

    def find_user(self, *args, **kwargs):
        """Returns a user matching the provided parameters."""
        raise NotImplementedError

    def toggle_active(self, user):
        """Toggles a user's active status. Always returns True."""
        user.active = not user.active
        self.put(user)
        return True

    def deactivate_user(self, user):
        """Deactivates a specified user. Returns `True` if a change was made.

        This will immediately disallow access to all endpoints that require
        authentication either via session or tokens.
        The user will not be able to log in again.

        :param user: The user to deactivate
        """
        if user.active:
            user.active = False
            self.put(user)
            return True
        return False

    def activate_user(self, user):
        """Activates a specified user. Returns `True` if a change was made.

        :param user: The user to activate
        """
        if not user.active:
            user.active = True
            self.put(user)
            return True
        return False

    def set_uniquifier(self, user, uniquifier=None):
        """ Set user's authentication token uniquifier.
        This will immediately render outstanding auth tokens,
        session cookies and remember cookies invalid.

        :param user: User to modify
        :param uniquifier: Unique value - if none then uuid.uuid4().hex is used

        This method is a no-op if the user model doesn't contain the attribute
        ``fs_uniquifier``

        .. versionadded:: 3.3.0
        """
        if not hasattr(user, "fs_uniquifier"):
            return
        if not uniquifier:
            uniquifier = uuid.uuid4().hex
        user.fs_uniquifier = uniquifier
        self.put(user)

    def create_user(self, **kwargs):
        """Creates and returns a new user from the given parameters.

        :kwparam email: required.
        :kwparam password:  Hashed password.
        :kwparam roles: list of roles to be added to user.
            Can be Role objects or strings

        .. danger::
           Be aware that whatever `password` is passed in will
           be stored directly in the DB. Do NOT pass in a plaintext password!
           Best practice is to pass in ``hash_password(plaintext_password)``.

           Furthermore, no validation is done on the password (e.g for minimum length).
           Best practice is to call
           ``app.security._password_validator(plaintext_password, True)``
           and look for a ``None`` return meaning the password conforms to the
           configured validations.

        The new user's ``active`` property will be set to ``True``
        unless explicitly set to ``False`` in `kwargs`.
        """
        kwargs = self._prepare_create_user_args(**kwargs)
        user = self.user_model(**kwargs)
        return self.put(user)

    def delete_user(self, user):
        """Deletes the specified user.

        :param user: The user to delete
        """
        self.delete(user)

    def reset_user_access(self, user):
        """
        Use this method to reset user authentication methods in the case of compromise.
        This will:

            * reset fs_uniquifier - which causes session cookie, remember cookie, auth
              tokens to be unusable
            * remove all unified signin TOTP secrets so those can't be used
            * remove all two-factor secrets so those can't be used

        Note that if using unified sign in and allow 'email' as a way to receive a code
        if the email is compromised - login is still possible. To handle this - it
        is better to deactivate the user.

        Note - this method isn't used directly by Flask-Security - it is provided
        as a helper for an applications administrative needs.

        Remember to call commit on DB if needed.

        .. versionadded:: 3.4.1
        """
        self.set_uniquifier(user)
        if hasattr(user, "us_totp_secrets"):
            self.us_reset(user)
        if hasattr(user, "tf_primary_method"):
            self.tf_reset(user)

    def tf_set(self, user, primary_method, totp_secret=None, phone=None):
        """ Set two-factor info into user record.
        This carefully only changes things if different.

        If totp_secret isn't provided - existing one won't be changed.
        If phone isn't provided, the existing phone number won't be changed.

        This could be called from an application to apiori setup a user for two factor
        without the user having to go through the setup process.

        To get a totp_secret - use ``app.security._totp_factory.generate_totp_secret()``

        .. versionadded: 3.4.1
        """

        changed = False
        if user.tf_primary_method != primary_method:
            user.tf_primary_method = primary_method
            changed = True
        if totp_secret and user.tf_totp_secret != totp_secret:
            user.tf_totp_secret = totp_secret
            changed = True
        if phone and user.tf_phone_number != phone:
            user.tf_phone_number = phone
            changed = True
        if changed:
            self.put(user)

    def tf_reset(self, user):
        """ Disable two-factor auth for user

        .. versionadded: 3.4.1
        """
        user.tf_primary_method = None
        user.tf_totp_secret = None
        user.tf_phone_number = None
        self.put(user)

    def us_get_totp_secrets(self, user):
        """ Return totp secrets.
        These are json encoded in the DB.

        Returns a dict with methods as keys and secrets as values.

        .. versionadded:: 3.4.0
        """
        if not user.us_totp_secrets:
            return {}
        return json.loads(user.us_totp_secrets)

    def us_put_totp_secrets(self, user, secrets):
        """ Save secrets. Assume to be a dict (or None)
        with keys as methods, and values as (encrypted) secrets.

        .. versionadded:: 3.4.0
        """
        user.us_totp_secrets = json.dumps(secrets) if secrets else None
        self.put(user)

    def us_set(self, user, method, totp_secret=None, phone=None):
        """ Set unified sign in info into user record.

        If totp_secret isn't provided - existing one won't be changed.
        If phone isn't provided, the existing phone number won't be changed.

        This could be called from an application to apiori setup a user for unified
        sign in without the user having to go through the setup process.

        To get a totp_secret - use ``app.security._totp_factory.generate_totp_secret()``

        .. versionadded: 3.4.1
        """

        if totp_secret:
            totp_secrets = self.us_get_totp_secrets(user)
            totp_secrets[method] = totp_secret
            self.us_put_totp_secrets(user, totp_secrets)
        if phone and user.us_phone_number != phone:
            user.us_phone_number = phone
            self.put(user)

    def us_reset(self, user):
        """ Disable unified sign in for user.
        Be aware that if "email" is an allowed way to receive codes, they
        will still work (as totp secrets are generated on the fly).
        This will disable authenticator app and SMS.

        .. versionadded: 3.4.1
        """
        user.us_totp_secrets = None
        user.us_phone_number = None
        self.put(user)


class SQLAlchemyUserDatastore(SQLAlchemyDatastore, UserDatastore):
    """A SQLAlchemy datastore implementation for Flask-Security that assumes the
    use of the Flask-SQLAlchemy extension.
    """

    def __init__(self, db, user_model):
        SQLAlchemyDatastore.__init__(self, db)
        UserDatastore.__init__(self, user_model)

    def get_user(self, identifier):
        from sqlalchemy import inspect
        from sqlalchemy.sql import sqltypes
        from sqlalchemy.dialects.postgresql import UUID as PSQL_UUID

        # To support both numeric, string, and UUID primary keys, and support
        # calling this routine with either a numeric value or a string or a UUID
        # we need to make sure the types basically match.
        # psycopg2 for example will complain if we attempt to 'get' a
        # numeric primary key with a string value.
        # TODO: other datastores don't support this - they assume the only
        # PK is user.id. That makes things easier but for backwards compat...
        ins = inspect(self.user_model)
        pk_type = ins.primary_key[0].type
        pk_isnumeric = isinstance(pk_type, sqltypes.Integer)
        pk_isuuid = isinstance(pk_type, PSQL_UUID)
        # Are they the same or NOT numeric nor UUID
        if (
                (pk_isnumeric and self._is_numeric(identifier))
                or (pk_isuuid and self._is_uuid(identifier))
                or (not pk_isnumeric and not pk_isuuid)
        ):
            rv = self.user_model.query.get(identifier)
            if rv is not None:
                return rv

    def find_user(self, **kwargs):
        query = self.user_model.query

        return query.filter_by(**kwargs).first()
