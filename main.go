package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"

	"github.com/gorilla/mux"
	"github.com/thedevsaddam/renderer"
)

// since we use containers for odoo and golang communicate each other we need to define the url head with host.docker.internal:port
// we cant use localhost since golang service will read it in local container
var OdoobaseURL = "http://host.docker.internal:8091/api/order"

func getOrderDetails(w http.ResponseWriter, r *http.Request) {
	// GET One Order details
	orderID := mux.Vars(r)["order_id"]
	urlPath := fmt.Sprintf("%s/%s", OdoobaseURL, orderID)
	request, err := http.NewRequest("GET", urlPath, nil)

	if err != nil {
		log.Fatal(err)
	}

	responseGeneric(w, r, request)
}

func responseGeneric(w http.ResponseWriter, r *http.Request, request *http.Request) {
	client := &http.Client{}
	Auth := r.Header.Get("Authorization")
	rnd := renderer.New()
	request.Header.Set("Authorization", Auth)

	response, err := client.Do(request)

	if err != nil {
		log.Fatal(err)
	}
	defer response.Body.Close()

	if response.StatusCode >= 500 {
		responseStruct := map[string]interface{}{
			"success": false,
			"message": "Internal Server Error",
		}
		rnd.JSON(w, http.StatusInternalServerError, responseStruct)
		return
	}

	responseData, err := ioutil.ReadAll(response.Body)
	if err != nil {
		log.Fatal(err)
	}

	var resultResp map[string]interface{}
	json.Unmarshal([]byte(responseData), &resultResp)
	rnd.JSON(w, http.StatusInternalServerError, resultResp)
}

func baseGenericFuncRequest(w http.ResponseWriter, r *http.Request, method string) {
	reqBody, _ := ioutil.ReadAll(r.Body)
	request, err := http.NewRequest(method, OdoobaseURL, bytes.NewBuffer(reqBody))

	if err != nil {
		log.Fatal(err)
	}
	responseGeneric(w, r, request)
}
func getListOrderDetails(w http.ResponseWriter, r *http.Request) {
	// GET Order Details Bulk
	baseGenericFuncRequest(w, r, "GET")
}

func createOrder(w http.ResponseWriter, r *http.Request) {
	// Create New Sale Order
	baseGenericFuncRequest(w, r, "POST")
}

func updateOrder(w http.ResponseWriter, r *http.Request) {
	// Update Existing Sale Order
	baseGenericFuncRequest(w, r, "PUT")
}

func testRunningService(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "This Service is Running")
}

func main() {
	router := mux.NewRouter().StrictSlash(true)
	router.HandleFunc("/order/{order_id}", getOrderDetails).Methods("GET")
	router.HandleFunc("/order", getListOrderDetails).Methods("GET")
	router.HandleFunc("/order", createOrder).Methods("POST")
	router.HandleFunc("/order", updateOrder).Methods("PUT")

	// test running service
	router.HandleFunc("/test", testRunningService)
	log.Fatal(http.ListenAndServe(":8080", router))

}
