# Chapter 3: Data, JSON, & APIs



<div align="center">
  <audio controls src="audio/03-DATA-AND-JSON.wav" title="Go Learning Audio Session" style="width: 100%; max-width: 400px; margin-bottom: 20px;"></audio>
  <p><i>Listen to the audio version above!</i></p>
</div>

HTML is great for building websites, but if you are building an API that mobile apps or React front-ends will talk to, you need a universal language. That language is **JSON** (JavaScript Object Notation).

In this chapter, we will learn how Go handles JSON—specifically, how it translates raw text into typed Go `structs` (Decoding), and how it translates Go `structs` back into text (Encoding).

## 1. The Power of Struct Tags

In Go, the shape of your data is defined by a `struct`. 
However, Go uses `PascalCase` (Capitalized) for public fields, while JSON traditionally uses `snake_case` or `camelCase`.

We use **Struct Tags** to tell Go how to map the fields.

```go
type User struct {
    // The struct tag `json:"id"` tells Go: "When you convert this to JSON, name it 'id'"
	ID        int    `json:"id"`
	FirstName string `json:"first_name"`
	LastName  string `json:"last_name"`
	
	// Omitempty means: "If this string is empty, just don't include it in the JSON at all"
	Email     string `json:"email,omitempty"`
	
	// A hyphen means: "NEVER include this in the JSON, keep it completely hidden"
	Password  string `json:"-"`
}
```

## 2. Returning JSON (Encoding)

When a client makes a `GET` request, you want to send them data.
You need to do two things:
1. Set the `Content-Type` header to `application/json` (so the browser knows how to parse it).
2. Marshal (Encode) the Go struct into JSON and send it.

```go
package main

import (
	"encoding/json"
	"net/http"
)

type Product struct {
	ID    int     `json:"id"`
	Name  string  `json:"name"`
	Price float64 `json:"price"`
}

func getProductHandler(w http.ResponseWriter, r *http.Request) {
	prod := Product{
		ID:    101,
		Name:  "Mechanical Keyboard",
		Price: 129.99,
	}

	// 1. Set the header BEFORE writing any data
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK) // Sends a 200 OK

	// 2. Encode and send
	// NewEncoder(w) connects directly to the ResponseWriter tray.
	// Encode(prod) translates the struct and immediately streams it out.
	err := json.NewEncoder(w).Encode(prod)
	if err != nil {
		http.Error(w, "Failed to encode JSON", http.StatusInternalServerError)
	}
}
```

*Output when visiting this route:*
```json
{
  "id": 101,
  "name": "Mechanical Keyboard",
  "price": 129.99
}
```

## 3. Receiving JSON (Decoding)

When a client makes a `POST` request (like submitting a registration form), they send a JSON body. You need to decode that body into a Go struct so you can work with it.

```go
type CreateUserRequest struct {
	Username string `json:"username"`
	Age      int    `json:"age"`
}

func createUserHandler(w http.ResponseWriter, r *http.Request) {
    // 1. Create an empty struct to hold the incoming data
	var input CreateUserRequest

    // 2. Decode the JSON body into the struct (using a pointer &input)
    // We use defer r.Body.Close() as a good habit to prevent memory leaks, 
    // though the server usually handles it.
	defer r.Body.Close()
	err := json.NewDecoder(r.Body).Decode(&input)
	
	if err != nil {
		// If the JSON is malformed (e.g., missing a comma, or wrong type)
		http.Error(w, "Bad Request: Invalid JSON", http.StatusBadRequest)
		return
	}

    // 3. We now have strongly-typed Go data!
    // We can validate it.
	if input.Age < 18 {
		http.Error(w, "Must be 18 or older", http.StatusBadRequest)
		return
	}

    // Success response
	w.WriteHeader(http.StatusCreated) // 201 Created
	w.Write([]byte("User " + input.Username + " created successfully!"))
}
```

## 4. Building a Reusable JSON Helper

Writing `w.Header().Set(...)` and `json.NewEncoder()` every single time gets tedious. Professional Go codebases usually have a `respondJSON` and `decodeJSON` helper function.

Let's build one:

```go
// helper.go

func RespondJSON(w http.ResponseWriter, status int, payload interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	
	if err := json.NewEncoder(w).Encode(payload); err != nil {
		log.Printf("Error encoding JSON response: %v", err)
	}
}

func RespondError(w http.ResponseWriter, status int, message string) {
    // We send errors as JSON objects too! {"error": "Message"}
	RespondJSON(w, status, map[string]string{"error": message})
}
```

Now our handlers look beautiful and clean:

```go
func getUserHandler(w http.ResponseWriter, r *http.Request) {
    user, err := fetchUserFromDatabase()
    if err != nil {
        RespondError(w, http.StatusNotFound, "User not found")
        return
    }
    
    RespondJSON(w, http.StatusOK, user)
}
```

### Summary of Chapter 3
You now know how to seamlessly pass data back and forth using Go structs and the `encoding/json` package, along with how to use Struct Tags to format the output.

But where does this data actually live? Right now, we're just hardcoding data in memory. We need to talk to a Database. And more importantly, we need to make sure we do it safely when thousands of people request it at the same time.

**Let's move on to [Chapter 4: Databases, State & Concurrency](04-DATABASES-AND-STATE.md)**
