from json import dumps


INVALID_JSON_PATH_MARK = 'INVALID'


def pbxport_post_save(instance, created, **kwargs):
    if created and not kwargs.get('raw', False):
        from .models import HistoricalPBXPort
        from .utils import (
            CrosspathPointEncoder,
            get_crosspath,
        )

        cp = get_crosspath(instance.pk)
        instance.json_path = dumps(cp, cls=CrosspathPointEncoder)
        instance.save()

        last_port_state = instance.history.values()[0]
        last_saved_historical_port = HistoricalPBXPort.objects.get(pk=last_port_state['history_id'])
        last_saved_historical_port.delete()

        last_port_state = instance.history.values()[0]
        last_saved_historical_port = HistoricalPBXPort.objects.get(pk=last_port_state['history_id'])
        last_saved_historical_port.save()


def crosspoint_pre_save(instance, **kwargs):
    def get_parent_and_invalidate_json_path(crosspoint):
        pbxport = crosspoint.get_parent()

        if pbxport:
            pbxport.json_path = INVALID_JSON_PATH_MARK
            pbxport.save_without_historical_record()

    if not kwargs.get('raw', False):
        if instance.destination is not None:
            get_parent_and_invalidate_json_path(instance.destination)

        if instance.pk is not None:
            get_parent_and_invalidate_json_path(instance)


def crosspoint_post_save(instance, **kwargs):
    if not kwargs.get('raw', False):
        from .models import PBXPort
        from .utils import CrosspathPointEncoder, get_crosspath

        invalid_ports = PBXPort.objects.filter(json_path=INVALID_JSON_PATH_MARK)

        cp = get_crosspath(tuple(port.pk for port in invalid_ports))

        for pbxport_point in cp:
            pbxport = PBXPort.objects.get(pk=pbxport_point.crosspoint_id)
            pbxport.json_path = dumps(pbxport_point, cls=CrosspathPointEncoder)
            pbxport.save()

        if len(instance.child_class) == 0:
            subclass = instance.get_subclass().__name__

            instance.child_class = subclass
            instance.save_without_historical_record()
