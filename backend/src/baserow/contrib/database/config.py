from django.apps import AppConfig

from baserow.core.registries import plugin_registry, application_type_registry

from .views.registries import view_type_registry
from .fields.registries import field_type_registry, field_converter_registry


class DatabaseConfig(AppConfig):
    name = 'baserow.contrib.database'

    def prevent_generated_model_for_registering(self):
        """
        A nasty hack that prevents a generated table model and related auto created
        models from being registered to the apps. When a model class is defined it
        will be registered to the apps, but we do not always want that to happen
        because models with the same class name can differ. They are also meant to be
        temporary. Removing the model from the cache does not work because if there
        are multiple requests at the same it is not removed from the cache on time
        which could result in hard failures. It is also hard to extend the
        django.apps.registry.apps so this hack extends the original `register_model`
        method and it will only call the original `register_model` method if the
        model is not a generated table model.

        If anyone has a better way to prevent the models from being registered then I
        am happy to hear about it! :)
        """

        original = self.apps.register_model

        def register_model(app_label, model):
            if (
                not hasattr(model, '_generated_table_model') and
                not hasattr(model._meta.auto_created, '_generated_table_model')
            ):
                return original(app_label, model)

        self.apps.register_model = register_model

    def ready(self):
        self.prevent_generated_model_for_registering()

        from .plugins import DatabasePlugin
        plugin_registry.register(DatabasePlugin())

        from .fields.field_types import (
            TextFieldType, LongTextFieldType, NumberFieldType, BooleanFieldType,
            DateFieldType, LinkRowFieldType
        )
        field_type_registry.register(TextFieldType())
        field_type_registry.register(LongTextFieldType())
        field_type_registry.register(NumberFieldType())
        field_type_registry.register(BooleanFieldType())
        field_type_registry.register(DateFieldType())
        field_type_registry.register(LinkRowFieldType())

        from .fields.field_converters import LinkRowFieldConverter
        field_converter_registry.register(LinkRowFieldConverter())

        from .views.view_types import GridViewType
        view_type_registry.register(GridViewType())

        from .application_types import DatabaseApplicationType
        application_type_registry.register(DatabaseApplicationType())
