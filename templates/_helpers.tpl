{{/* common labels */}}
{{- define "haystack.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{- define "haystack.name" -}}
{{ .Chart.Name }}
{{- end -}}
