# A General Framework for Debugging Kubernetes Connectivity Issues
## 1. Identify the Components Involved

Source: The pod or service that’s trying to make the connection

Target: The pod or service that the source is trying to reach

This helps you focus on what part of the system you need to debug.

## 2. Validate Pod and Service Status
### 2.1. Check Pods
Are the source and target pods running?

```bash
kubectl get pods -n <namespace>
```
All pods should show Running and the READY column should show the correct number of containers.
Check pod logs for any errors related to readiness or network issues:

```bash
kubectl logs <pod-name> -n <namespace>
```
### 2.2. Check Services
Is the service created and exposing the correct ports?

```bash
kubectl get svc -n <namespace>
```
The service should show the correct ClusterIP and ports.
Example output:
```scss
NAME   TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)    AGE
echo   ClusterIP   10.0.0.1     <none>        7070/TCP   10m
```

Is the service mapped to the correct target port (the container's port)?

```bash
kubectl describe svc <service-name> -n <namespace>
```
This will show the port mappings. Ensure the service port matches the container's targetPort.
## 3. Networking Check: DNS and Reachability
### 3.1. DNS Resolution
Does the source pod resolve the target service’s DNS correctly?
You can run a DNS resolution test from the source pod:
```bash
kubectl run -it --rm --restart=Never dns-test --image=busybox -- nslookup <service-name>.<namespace>.svc.cluster.local
```
This will test if the target service resolves to a valid ClusterIP.
If DNS fails, ensure that the CoreDNS pods are running and healthy:
```bash
kubectl get pods -n kube-system -l k8s-app=kube-dns
```
### 3.2. Ping and Port Checks
Can the source pod reach the target service via IP or hostname?

Try pinging the service IP or pod IP from the source pod:
```bash
kubectl exec <source-pod> -- ping <service-ip>
```
Test the service port (e.g., 7070) using curl or nc from the source pod to check if the port is open:

```bash
kubectl exec <source-pod> -- nc -zv <target-service-ip> 7070
```
If these fail, there might be a network or routing issue between the pods.

## 4. Service Mesh and Network Policies
### 4.1. Istio or mTLS Settings
Is Istio or another service mesh enforcing traffic policies like mTLS?

Check if mutual TLS (mTLS) is enabled in the namespace or globally using PeerAuthentication:
```bash
kubectl get peerauthentication --all-namespaces
```
Are there any virtual services, destination rules, or gateways affecting traffic?

Verify Istio's configuration for the namespace by checking these resources:
```bash
kubectl get virtualservice,destinationrule,gateway -n <namespace>
```
### 4.2. Network Policies
Are there network policies blocking traffic?
Check if any NetworkPolicy resources are applied that could restrict communication between namespaces or pods:
```bash
kubectl get networkpolicy -n <namespace>
```
Inspect the rules to ensure that the target pod or service is allowed to receive traffic from the source pod.
## 5. Pod-Level Debugging
### 5.1. Check Container Ports
Ensure that the pod is listening on the correct port by checking the container spec:
```bash
kubectl describe pod <pod-name> -n <namespace>
```
Verify that the container has the expected port open.
### 5.2. Test Connectivity from the Pod
Run curl or grpcurl directly inside the pod to test reachability. For example, if you're testing gRPC connectivity:
```bash
kubectl exec <source-pod> -- grpcurl -plaintext <service-ip>:7070 proto.EchoTestService/ForwardEcho
```
## 6. Inspect Pod Readiness and Liveness
Are the pods ready to receive traffic?

Kubernetes uses readiness probes to determine if a pod can receive traffic. If the pod isn’t ready, traffic won’t be routed to it:
```bash
kubectl describe pod <pod-name> -n <namespace>
```
Look for readiness or liveness probe failures.
Do the pods have any CrashLoopBackOff issues?

Pods in a CrashLoopBackOff state indicate there’s a problem starting the application.
## 7. Debugging at the Network Layer
### 7.1. Use kubectl port-forward for Port Debugging
Use kubectl port-forward to tunnel into a pod and check if it's correctly listening on a port:
```bash
kubectl port-forward <pod-name> 8080:7070
```
### 7.2. Look at Network Traffic with Tools
You can use tools like tcpdump or Wireshark to monitor traffic between the source and target pod.
Alternatively, use Kubernetes NetworkPolicy logs or Istio’s Envoy proxy logs (if using Istio) to track where traffic might be getting blocked.

## 8. Final Step: Cluster-Wide Issues
If nothing seems wrong at the pod or service level, consider cluster-wide issues like:

Cluster DNS outages.
Node-level issues (e.g., nodes are unhealthy, or networking on the nodes is misconfigured).
IP conflicts or CNI (Container Network Interface) issues (check the CNI plugin's health, such as Calico, Flannel, etc.).
Use kubectl get nodes and check the status of the nodes to ensure they're all healthy.
