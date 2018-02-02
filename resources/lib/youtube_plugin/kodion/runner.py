__author__ = 'bromix'

__all__ = ['run']

import copy
from .impl import Runner
from .impl import Context

__RUNNER__ = Runner()


def run(provider, context=None):
    if not context:
        context = Context(plugin_id='plugin.video.youtube')

    context.log_debug('Starting Kodion framework by bromix...')
    python_version = 'Unknown version of Python'
    try:
        import platform

        python_version = str(platform.python_version())
        python_version = 'Python %s' % python_version
    except:
        # do nothing
        pass

    version = context.get_system_version()
    name = context.get_name()
    addon_version = context.get_version()
    context.log_notice('Running: %s (%s) on %s with %s' % (name, addon_version, version, python_version))
    context.log_debug('Path: "%s' % context.get_path())
    redacted = '<redacted>'
    context_params = copy.deepcopy(context.get_params())
    if 'api_key' in context_params:
        context_params['api_key'] = redacted
    if 'client_id' in context_params:
        context_params['client_id'] = redacted
    if 'client_secret' in context_params:
        context_params['client_secret'] = redacted
    context.log_debug('Params: "%s"' % str(context_params))
    __RUNNER__.run(provider, context)
    provider.tear_down(context)
    context.log_debug('Shutdown of Kodion')
