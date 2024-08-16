#!/usr/bin/env bash

set -x -e

#{% if old_tag is defined and config.docker_del_img is defined %}
#{{ config.docker_del_img }} {{ config.registry_name }}/{{ config.project_id }}/ekatra:{{ old_tag }}
#{% endif %}

docker tag demo/ekatra {{ config.registry_name }}/{{ config.project_id }}/ekatra
#:{{ new_tag }}
{{ config.docker_push }} {{ config.registry_name }}/{{ config.project_id }}/ekatra
#:{{ new_tag }}

{% if config.docker_img_list is defined %}
{{ config.docker_img_list }} {{ config.registry_name }}/{{ config.project_id }}/ekatra
{% endif %}

