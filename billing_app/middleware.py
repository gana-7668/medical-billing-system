from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

SAFE_PATH_PREFIXES = (
    '/login',
    '/logout',
    '/admin',
    '/static',
)


class PerTabAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user = getattr(request, 'user', None)
        path = request.path
        if not user or not user.is_authenticated:
            return None
        if any(path.startswith(p) for p in SAFE_PATH_PREFIXES):
            return None

        # NOTE: Allow normal session to persist; do not force logout on each refresh

        if 'tab' in request.GET:
            return None

        # Inject a minimal HTML that generates a per-tab id and reloads with ?tab=
        current_url = request.get_full_path()
        html = f"""
<!DOCTYPE html>
<html><head><meta charset='utf-8'><title>Loading…</title></head>
<body>
<script>
  (function() {{
    try {{
      var tid = sessionStorage.getItem('tab_id');
      if (!tid) {{
        // Simple UUIDv4 generator
        tid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {{
          var r = Math.random()*16|0, v = c == 'x' ? r : (r&0x3|0x8);
          return v.toString(16);
        }});
        sessionStorage.setItem('tab_id', tid);
      }}
      var url = new URL(window.location.href);
      url.searchParams.set('tab', tid);
      window.location.replace(url.toString());
    }} catch(e) {{
      window.location.replace('{current_url}');
    }}
  }})();
  </script>
</body></html>
"""
        return HttpResponse(html)


