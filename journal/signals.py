from json import dumps


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
