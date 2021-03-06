<?php

namespace app\models;

use mako\database\midgard\ORM;
use mako\database\midgard\relations\BelongsTo;
use mako\database\midgard\relations\HasOne;
use mako\database\midgard\traits\TimestampedTrait;

class Invitation extends ORM
{
	use TimestampedTrait;

	public function archiveType(): BelongsTo
	{
		return $this->belongsTo(ArchiveType::class);
	}

	public function metsFile(): HasOne
	{
		return $this->hasOne(MetsFile::class);
	}
}
