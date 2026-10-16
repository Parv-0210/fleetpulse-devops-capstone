{{/* Chart name */}}
{{- define "fleetpulse.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/* Fully qualified app name (release-aware) */}}
{{- define "fleetpulse.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{- define "fleetpulse.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/* Common labels */}}
{{- define "fleetpulse.labels" -}}
helm.sh/chart: {{ include "fleetpulse.chart" . }}
app.kubernetes.io/name: {{ include "fleetpulse.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: fleetpulse
{{- end -}}

{{/* Selector labels for a component: include "fleetpulse.selectorLabels" (dict "root" . "component" "backend") */}}
{{- define "fleetpulse.selectorLabels" -}}
app.kubernetes.io/name: {{ include "fleetpulse.name" .root }}
app.kubernetes.io/instance: {{ .root.Release.Name }}
app.kubernetes.io/component: {{ .component }}
{{- end -}}

{{/* Component resource names */}}
{{- define "fleetpulse.backend.name" -}}{{ include "fleetpulse.fullname" . }}-backend{{- end -}}
{{- define "fleetpulse.frontend.name" -}}{{ include "fleetpulse.fullname" . }}-frontend{{- end -}}
{{- define "fleetpulse.postgres.name" -}}{{ include "fleetpulse.fullname" . }}-postgres{{- end -}}
{{- define "fleetpulse.secret.name" -}}{{ default (printf "%s-secrets" (include "fleetpulse.fullname" .)) .Values.postgres.existingSecret }}{{- end -}}

{{/* Image references */}}
{{- define "fleetpulse.backend.image" -}}
{{- $repo := default (printf "%s/%s/fleetpulse-backend" .Values.image.registry .Values.image.owner) .Values.backend.repository -}}
{{- printf "%s:%s" $repo (default .Chart.AppVersion .Values.backend.tag) -}}
{{- end -}}

{{- define "fleetpulse.frontend.image" -}}
{{- $repo := default (printf "%s/%s/fleetpulse-frontend" .Values.image.registry .Values.image.owner) .Values.frontend.repository -}}
{{- printf "%s:%s" $repo (default .Chart.AppVersion .Values.frontend.tag) -}}
{{- end -}}

{{/* Database URL used by the backend (in-cluster Postgres) */}}
{{- define "fleetpulse.databaseUrl" -}}
postgresql+psycopg://{{ .Values.postgres.username }}:{{ .Values.postgres.password }}@{{ include "fleetpulse.postgres.name" . }}:5432/{{ .Values.postgres.database }}
{{- end -}}

{{/* Environment block shared by the migrate init container and the API container */}}
{{- define "fleetpulse.backend.env" -}}
- name: DATABASE_URL
  valueFrom:
    secretKeyRef:
      name: {{ include "fleetpulse.secret.name" . }}
      key: DATABASE_URL
envFrom:
{{- end -}}
