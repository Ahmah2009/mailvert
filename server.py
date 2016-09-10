#!flask/bin/python
from flask import Flask,jsonify,request
import re
import socket
import smtplib
import dns.resolver


app = Flask(__name__)


@app.route('/v1/', methods=['GET'])

def ver_email():
    email= request.args.get('email')
    print email
    fromAddress = 'we@la.com'
    addressToVerify = str(email)
    # check email syntax using regex
    regex = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'
    match = re.match(regex, addressToVerify)
    if match == None:
    	return jsonify({'result': 'Faild'})

    # get The dns information
    # 1- get the domain, usually after '@'
    # 2- dig domain mx, will return the list of mx records
    # 3- get the first mx record 
    # 4- if lookup for mx return with error, return Faild
    splitAddress = addressToVerify.split('@')
    domain = str(splitAddress[1])
    print('Domain:', domain)

    try:
        records = dns.resolver.query(domain, 'MX')
    except dns.resolver.NXDOMAIN:
        print "No such domain"
        return jsonify({'result': 'Faild'})
    except dns.resolver.Timeout:
        print "Timed out while resolving"
        return jsonify({'result': 'Faild'})
    except dns.exception.DNSException:
        print "Unhandled exception"
        return jsonify({'result': 'Faild'})

    if len(records)==0:
        return jsonify({'result': 'Faild'})

    # 1- inti new smtp client 
    # 2- set debug level to 0 to get full output 
    # 3- connect to mx record host address 
    # 4- send helo or ehlo to start communcation with smtp server 
    # 5- send mail from to mimitat send new email proccess
    # 6- send recipient addresses to check if it known to the mail server
    # 7- send quit to smtp to close connection the smtp server 
    
    try:
        mxRecord = records[0].exchange
        mxRecord = str(mxRecord)
        host = socket.gethostname()
        server = smtplib.SMTP()
        server.set_debuglevel(0)
        server.connect(mxRecord)
        server.helo(host)
        server.mail(fromAddress)
        code, message = server.rcpt(str(addressToVerify))
        server.quit()
    except Exception:
        code=-1 

    if code == 250:
    	print('Success')
        return jsonify({'result': 'Success'})
    else:
    	print('Bad')
        return jsonify({'result': 'Faild'})

if __name__ == '__main__':
    app.run(debug=True)

