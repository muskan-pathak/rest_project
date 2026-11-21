from django.db import migrations, models
import django.db.models.deletion
def migrate_project_data(apps, schema_editor):
    Project = apps.get_model('users', 'Project')
    ProjectType = apps.get_model('users', 'ProjectType')
    ProjectStatus = apps.get_model('users', 'ProjectStatus')

    db = schema_editor.connection.alias

    projects = Project.objects.using(db).all()

    for project in projects:

        # Project Type mapping
        old_type = project.project_type

        if old_type and old_type.strip().lower() != "null":
            old_type = old_type.strip()

            project_type = ProjectType.objects.using(db).filter(
                name__iexact=old_type
            ).first()

            if not project_type:
                project_type = ProjectType.objects.using(db).create(
                    name=old_type.title(),
                    is_default=False
                )

            project.project_type_fk_id = project_type.id

        # Project Status mapping
        old_status = project.project_status

        if old_status and old_status.strip():
            old_status = old_status.strip()

            project_status = ProjectStatus.objects.using(db).filter(
                name__iexact=old_status
            ).first()

            if not project_status:
                project_status = ProjectStatus.objects.using(db).create(
                    name=old_status.title(),
                    is_default=False
                )

            project.project_status_fk_id = project_status.id

        project.save(
            using=db,
            update_fields=['project_type_fk', 'project_status_fk']
        )


def reverse_project_data(apps, schema_editor):
    Project = apps.get_model('users', 'Project')

    db = schema_editor.connection.alias

    for project in Project.objects.using(db).all():

        if project.project_type_fk_id:
            project.project_type = project.project_type_fk.name

        if project.project_status_fk_id:
            project.project_status = project.project_status_fk.name

        project.save(
            using=db,
            update_fields=['project_type', 'project_status']
        )


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0036_projectstatus_projecttype'),
    ]

    operations = [

        migrations.AddField(
            model_name='project',
            name='project_type_fk',
            field=models.ForeignKey(
                to='users.projecttype',
                on_delete=django.db.models.deletion.PROTECT,
                related_name='projects',
                null=True,
                blank=True
            ),
        ),

        migrations.AddField(
            model_name='project',
            name='project_status_fk',
            field=models.ForeignKey(
                to='users.projectstatus',
                on_delete=django.db.models.deletion.PROTECT,
                related_name='projects',
                null=True,
                blank=True
            ),
        ),

        migrations.RunPython(
            migrate_project_data,
            reverse_project_data
        ),

        migrations.RemoveField(
            model_name='project',
            name='project_type',
        ),

        migrations.RemoveField(
            model_name='project',
            name='project_status',
        ),

        migrations.RenameField(
            model_name='project',
            old_name='project_type_fk',
            new_name='project_type',
        ),

        migrations.RenameField(
            model_name='project',
            old_name='project_status_fk',
            new_name='project_status',
        ),
    ]

