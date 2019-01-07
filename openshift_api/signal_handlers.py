from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from .models import Role, Package, Cluster


@receiver(post_save, sender=Cluster)
def on_cluster_save(sender, instance=None, **kwargs):
    if instance and instance.template:
        instance.create_roles()
        instance.create_node_localhost()


def auto_lookup_packages():
    try:
        Package.lookup()
    except:
        pass


auto_lookup_packages()
