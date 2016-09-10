# mailvert

## Background: 
TO validate email address (dig, telnet): 
  1. find the mx record of the domain
   
		dig example.com mx
  2. connect to mx host address
  
		telnet mail.example.com 25
  3. send helo 
  
		HELO local.domain.name
  4. send send address 
  
		MAIL FROM: mail@domain.ext
  5. send rcpt with the needed mail address
  		
  		```sh
		RCPT TO: mail@otherdomain.ext
		```

  6. handle response
