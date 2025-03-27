# Download Minikube
Invoke-WebRequest -Uri "https://storage.googleapis.com/minikube/releases/latest/minikube-windows-amd64.exe" -OutFile "minikube.exe"

# Add Minikube to PATH
$env:Path += ";."
