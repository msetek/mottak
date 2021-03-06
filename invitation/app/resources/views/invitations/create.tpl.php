{% extends:'body' %}

{% block:content %}
{% if($input !== null) %}
	<div class="alert alert-info" role="alert">
		Vennligst kontroller at all informasjon stemmer før du går videre.
	</div>
{% elseif($failed_to_parse) %}
	<div class="alert alert-warning" role="alert">
		Vi greide ikke å parse XML-filen. Vennligst fyll ut alle felt før du går videre.
	</div>
{% endif %}
<form method="post">
	<div class="form-group">
		<label for="name">Navn</label>
		<input type="text" name="name" id="name" class="form-control" placeholder="Fyll ut navn" value="{{$_old_['name'], default: $input['name'] ?? ''}}">
	</div>
	<div class="form-group">
		<label for="email">E-postadresse</label>
		<input  type="text" name="email" id="email" class="form-control" placeholder="Fyll ut e-postadresse" value="{{$_old_['email'], default: $input['email'] ?? ''}}">
	</div>
	<div class="form-group">
		<label for="uuid">UUID</label>
		<input  type="text" name="uuid" id="uuid" class="form-control" placeholder="Fyll ut UUID" value="{{$_old_['uuid'], default: $input['uuid'] ?? ''}}">
	</div>
	<div class="form-group">
		<label for="checksum">Sjekksum</label>
		<input  type="text" name="checksum" id="checksum" class="form-control" placeholder="Fyll ut sjekksumm" value="{{$_old_['checksum'], default: $input['checksum'] ?? ''}}">
	</div>
	<div class="form-group">
		<label for="archive_type_id">Arkivtype</label>
		<select  name="archive_type_id" id="archive_type_id" class="form-control" placeholder="Velg arkivtype">
			<option disabled{% if(empty($_old_['archive_type_id'])) %} selected{% endif %}>Velg arkivtype</option>
			{% foreach($archive_types as $archive_type) %}
				<option value="{{$archive_type->id}}"{% if(!empty($_old_['archive_type_id']) && $_old_['archive_type_id'] === (string) $archive_type->id) %} selected{% endif %}>{{$archive_type->type}}</option>
			{% endforeach %}
		</select>
	</div>
	<div class="form-group">
		<div class="custom-control custom-radio">
			<input type="radio" id="is_sensitive1" name="is_sensitive" class="custom-control-input" value="0"{% if(empty($_old_['is_sensitive']) || $_old_['is_sensitive'] === '0') %} checked{% endif %}>
			<label class="custom-control-label" for="is_sensitive1">Arkivet inneholder <em>ikke</em> sensitiv informasjon.</label>
		</div>
		<div class="custom-control custom-radio">
			<input type="radio" id="is_sensitive2" name="is_sensitive" class="custom-control-input" value="1"{% if(!empty($_old_['is_sensitive']) && $_old_['is_sensitive'] === '1') %} checked{% endif %}>
			<label class="custom-control-label" for="is_sensitive2">Arkivet inneholder sensitiv informasjon.</label>
		</div>
	</div>
	<button type="submit" class="btn btn-primary">Gå videre</button>
</form>
{% endblock %}
