FROM golang:1.12.0-alpine3.9

# since we want to use go get we need to add git
RUN apk add git

# download gorilla/mux for http request that we use in main.go 
RUN go get github.com/gorilla/mux
RUN go get github.com/thedevsaddam/renderer

# standard run 
RUN mkdir /app
ADD . /app
WORKDIR /app
RUN go build -o main .
CMD ["/app/main"]