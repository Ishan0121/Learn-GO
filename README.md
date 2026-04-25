# 🚀 Aetheris Go Learning Repository

Welcome to the **Aetheris Go Learning Repository**. This directory contains comprehensive resources, tutorials, and practical projects designed to help you master the Go (Golang) programming language.

## 📂 Learning Paths

The material here is organized into two distinct learning approaches:

### 1. [By Practice (`/ByPract`)](./ByPract/)
This track focuses on learning Go by building practical, real-world applications from scratch.
* **[The Ultimate Guide to Building Web Servers in Go](./ByPract/WebServer/README.md)**: A comprehensive deep-dive into building backend web services. It covers everything from standard library `net/http` basics and Go 1.22 routing to advanced patterns, middlewares, database connections, and concurrency.

### 2. [By Question / Example (`/ByQ`)](./ByQ/README.md)
This track provides bite-sized, atomic lessons covering specific Go concepts, syntax, and standard library features. It is structured sequentially from absolute beginner topics to advanced engineering concepts.
* **[Go Concept Index](./ByQ/README.md)**: Contains 85+ individual modules covering topics such as:
  * Core Syntax (Variables, Slices, Structs, Maps)
  * Concurrency (Goroutines, Channels, WaitGroups, Mutexes)
  * Standard Library (JSON, Time, RegEx, File I/O)
  * Advanced Concepts (Context, Generics, Testing)

## 🎧 Audio Generation (`generate_audio.py`)
This repository includes a custom text-to-speech engine wrapper (`generate_audio.py`) that converts these markdown guides into high-quality audio sessions (`.wav` files) using Kokoro TTS. This allows for a multi-modal learning experience where you can listen to the guides while practicing the code.
