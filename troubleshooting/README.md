# Troubleshooting lab

Two deliberately broken manifests used in the final demo to show a live investigation.

| Scenario | Symptom | Investigation | Root cause |
|---|---|---|---|
| `broken-image.yaml` | Pod stuck in `ImagePullBackOff` | `kubectl describe pod`, `kubectl get events --sort-by=.lastTimestamp` | image tag does not exist in GHCR |
| `broken-service.yaml` | `curl` to the Service times out | `kubectl get endpoints`, `kubectl get pods --show-labels` | Service selector matches no Pod labels |

```bash
kubectl apply -f troubleshooting/broken-image.yaml
kubectl get pods -n fleetpulse -w
kubectl describe pod -l app=broken-image -n fleetpulse | tail -15

kubectl apply -f troubleshooting/broken-service.yaml
kubectl get endpoints broken-backend -n fleetpulse
kubectl get pods -n fleetpulse --show-labels | grep backend

# clean up
kubectl delete -f troubleshooting/
```

Bonus scenarios to try live: scale PostgreSQL to 0 and watch `/ready` flip the backend pods to
`0/1 READY` (readiness vs liveness), or set a wrong `DATABASE_URL` and read the init container logs
with `kubectl logs <pod> -c migrate`.
