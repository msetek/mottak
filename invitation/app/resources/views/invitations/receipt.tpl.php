{% extends:'body' %}

{% block:content %}
<div class="card">
	<div class="card-body">
		<p>Du kan nå laste opp {{$invitation->uuid}}-arkivet med Uploader.</p>
		<p><a href="{{$url}}" class="btn btn-primary btn-lg btn-block">Start Uploader</a></p>
	</div>
</div>
{% endblock %}
