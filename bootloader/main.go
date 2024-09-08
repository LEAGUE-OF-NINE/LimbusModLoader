package main

import (
	"crypto/sha1"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
)

func main() {
	// Get the current executable path
	execPath, err := os.Executable()
	if err != nil {
		fmt.Println("Error getting executable path:", err)
		return
	}

	// Change directory to the "_internal" directory relative to the current executable path
	internalDir := filepath.Join(filepath.Dir(execPath), "_internal")
	err = os.Chdir(internalDir)
	if err != nil {
		fmt.Println("Error changing directory:", err)
		return
	}

	// Check the integrity of "venv/Bins/python.exe" using SHA-256
	pythonExePath := filepath.Join(internalDir, "venv", "Bins", "python.exe")
	expectedHash := "eadbea44eb33bb292dfd53905e599bb5f8c3bb9e"
	actualHash, err := calculateSHA256(pythonExePath)
	if err != nil {
		fmt.Println("Error calculating hash:", err)
		return
	}
	if actualHash != expectedHash {
		fmt.Println("Integrity check failed. Expected hash:", expectedHash, "Actual hash:", actualHash)
		return
	}

	// Set the environment variable "PYTHONPATH"
	pythonPath := filepath.Join(internalDir, "venv", "Lib", "site-packages")
	err = os.Setenv("PYTHONPATH", pythonPath)
	if err != nil {
		fmt.Println("Error setting environment variable:", err)
		return
	}

	// Run the Python script "main.py"
	args := os.Args
	args[0] = "main.py"
	cmd := exec.Command(pythonExePath, args...)
	fmt.Println("Running Python script:", cmd)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	err = cmd.Run()
	if err != nil {
		fmt.Println("Error running Python script:", err)
		return
	}
}

func calculateSHA256(filePath string) (string, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return "", err
	}
	defer file.Close()

	hash := sha1.New()
	if _, err := io.Copy(hash, file); err != nil {
		return "", err
	}

	hashInBytes := hash.Sum(nil)
	return fmt.Sprintf("%x", hashInBytes), nil
}
