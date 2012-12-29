#!/usr/bin/python


import argparse
import boto
import sys
import time

from boto.ec2.connection import EC2Connection
from boto.route53.record import ResourceRecordSets

# Maximum number of instances allowed 
max_inst = 100;

# Amazon keys
AWS_ACCESS_KEY_ID=""
AWS_SECRET_ACCESS_KEY=""

# Open Flow training AMI
us_east_ami="ami-5df57734"
ami=us_east_ami


# Default instance type
inst_type="t1.micro"

prefix="vm"
domain_name="training.incntre.org"
domain_id="Z38ADT7WMJM3BC"



def start_instances(name,num):
        i = 0
	# EC2 connection
        conn = EC2Connection(AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)

	# Route53 Connection
	rt53_conn = boto.connect_route53(AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY)
	changes = ResourceRecordSets(rt53_conn,domain_id) 

	
        # Start instances 
        print "Starting %d Instances" % (num)
        res = conn.run_instances(us_east_ami, max_count=num, min_count=num, key_name='master-chsmall', instance_type=inst_type)

	
        # Tag and setup DNS once instances are running
        while i < num:
                # Wait until running
                instance = res.instances[i]
                status = instance.update()
                while status == 'pending':
                        time.sleep(1)
                        status = instance.update()
                if status == 'running':
                        tag_name = prefix + str(i+1)
			print "VM %s started" % tag_name
                        # add tag to VM in EC2 so we can find it in the console
                        instance.add_tag("Name",tag_name)
                        instance.add_tag("Purpose",name)
                        # Add DNS
                        fqdn = tag_name + "." + domain_name
			ec2_fqdn = instance.public_dns_name
                        print "Adding DNS for name %s to %s" % (fqdn,ec2_fqdn)
			change = changes.add_change("CREATE", fqdn , "CNAME")
			change.add_value(ec2_fqdn)
		# increment to next instance
		i=i+1

	changes.commit()
        print "VMs started and DNS created"




# Parse arguments
# of_training start <name> <num of inst>
# of_training stop <name>
# of_training status <name>

parser = argparse.ArgumentParser()
parser.add_argument("cmd", action="store")
parser.add_argument("name", action="store")
parser.add_argument("--num", type=int)
args = parser.parse_args()


if args.cmd == "start":
    if args.num <= 0:
    	print "Need pos # of instances (%d)" % args.num
	sys.exit(1)
    if args.num > max_inst:
	print "Max instances %d exceeded %d" %  (max_inst,args.num)
	sys.exit(1)
    if args.num:
	print "start_instances %s %d" % (args.name,args.num)
	start_instances(args.name,args.num)
	sys.exit(0)
    
if args.cmd == "stop":
	print "stop_instances %s" % (name) 
	sys.exit(0)

else: 
	print "Unknown command"
	sys.exit(1)






			
	
	



