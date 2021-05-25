# boto3-automate-ec2
Demonstration based on assessment requirement

## Prerequisites

**Software**

* Python 3<br>
* boto3<br>
* AWS Command Line Interface(Configure using Access Keys)<br>

## Content-Files

**ec2_setup.py**

* This python script enables creation of a VPC ,subnet and creates an EC2 instance with two users with configured public keys and  two volumes.

**test.yaml**
	
* Has the configuration required to set up EC2 instance and the requirements.
  
  
## How to run the program

* Download AWS CLI ,configue AWS credentials .
* For this create a new user and for example i created a developer account as it is a best practice not to use root account .

## Steps to configure AWS credentials

* Go to command line where you just install AWS cli and type `aws configure`
* Enter AWS Access Key ID,AWS Secret Access Key ,the default region and the output format.

**Once complete run python3 ec2_setup.py**