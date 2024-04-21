import shutil
from django import template

register = template.Library()


@register.simple_tag
def storage_info():
    total, used, free = shutil.disk_usage("./media")

    return {
        ' * total': f"{round(total / (1024**3))}GB",
        ' * used': f"{round(used / (1024**3))}GB",
        ' * free': f"{round(free / (1024**3))}GB",
    }
