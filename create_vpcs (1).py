import boto3
import time 

# ami-0cf10cdf9fcd62d37


# Functions that create the route table associted with the subnets 
def create_private_route_table(id, num):
    private = client.create_route_table(
            VpcId = id,
            TagSpecifications=[{'ResourceType': 'route-table','Tags': [{'Key': 'Name','Value': 'PrivateRouteTable' + str(num)}]}])
    return (private)



# Functions that attach internet gateaway to a VPC 
def attach_internet_gateway (gateway_id, VpcID):
    ig = client.attach_internet_gateway(
            InternetGatewayId = gateway_id,
            VpcId = VpcID
        )
    return (ig)
    
    
# Function that creates VPC Peering Connection 
def vpc_peering():
    # create vpc peering connection 
    vpc_pc = client.create_vpc_peering_connection(
            VpcId = VPC_A_id,
            PeerVpcId = VPC_B_id,
            TagSpecifications=[{'ResourceType': 'vpc-peering-connection','Tags': [{'Key': 'Name','Value': 'VPC Peering'}]}]
        )
    accept = client.accept_vpc_peering_connection(
            VpcPeeringConnectionId = vpc_pc['VpcPeeringConnection']['VpcPeeringConnectionId']
        )
    return (accept)
 


# Function that creates a nat_gateway 
def nat_gateway(subnet, Allocation, num):
    nat = client.create_nat_gateway(
            SubnetId = subnet,
            AllocationId = Allocation,
            TagSpecifications=[{'ResourceType': 'natgateway','Tags': [{'Key': 'Name','Value': 'nat gateway' + str(num)}]}])
    return (nat)
    
    
# Function that creates a route to the internet gateway 
def create_route_1 (id, gateway):
    route = client.create_route(
        RouteTableId= id,
        DestinationCidrBlock='0.0.0.0/0',
        GatewayId= gateway,
    )
    return (route)
    
    
# Function the creates a route to the VPC B vis VPC Peering 
def create_route_2 (id, pc):
    route = client.create_route(
        RouteTableId= id,
        DestinationCidrBlock='192.168.0.0/16',
        VpcPeeringConnectionId = pc['VpcPeeringConnection']['VpcPeeringConnectionId']
    )
    return (route)
    
# function that creates route to vpc a via VPC Peering 
def create_route_3 (id, pc):
    route = client.create_route(
        RouteTableId= id,
        DestinationCidrBlock='10.0.0.0/16',
        VpcPeeringConnectionId = pc['VpcPeeringConnection']['VpcPeeringConnectionId']
    )
    return (route)


# Creates route to nat gateway 
def create_route_4 (id, nat):
    route = client.create_route(
            RouteTableId = id,
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId = nat
        )
    return (route)


## Function designed to associate a route table to a subnet 

# associate for public subnets 
def associate (id):
    client.associate_route_table(
            RouteTableId = id,
            SubnetId = SubnetID,
        )

# Functions to Create two Subnets one in VPC A and one in VPC B 
def create_subnets_VpcA():
    subnetList = []
    for i in range (3):
        Subnet = client.create_subnet (
            CidrBlock = '10.0.' + str(i + 1) +'.0/24',
            VpcId = VPC_A_id,
        )
        if (i < 2):
            client.modify_subnet_attribute(
                SubnetId=Subnet['Subnet']['SubnetId'],
                MapPublicIpOnLaunch={'Value': True},
            )
        
        subnetList.append(Subnet)
    return (subnetList)
    
    
    
def create_subnets_VpcB():
    subnetList = []
    for i in range (3):
        Subnet = client.create_subnet (
            CidrBlock = '192.168.' + str(i + 1) + '.0/24',
            VpcId = VPC_B_id
        )
        if (i < 2):
            client.modify_subnet_attribute(
                SubnetId=Subnet['Subnet']['SubnetId'],
                MapPublicIpOnLaunch={'Value': True},
            )
        subnetList.append(Subnet)
    return(subnetList)
    

## These function define the creation of Security Groups   

# Allows ssh and http from anywhere 
def create_security_group1 (id):
    sg = client.create_security_group(
        Description = "Allow SSH and HTTP",
        GroupName ="Launch Wizard 1",
        VpcId = id
    )
    GroupId = sg['GroupId']
    client.authorize_security_group_ingress(
            GroupId = GroupId,
            IpPermissions = [{'IpProtocol': 'tcp', 'FromPort': 22,'ToPort': 22, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}]
        )
    client.authorize_security_group_ingress(
            GroupId = GroupId,
            IpPermissions = [{'IpProtocol': 'tcp', 'FromPort': 80,'ToPort': 80, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}]
        )
        
    return (sg)  
    
    
    
## This function Creates an instance 
def create_instance(Id, Sg_Id, bootstrap):
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    instances = ec2_client.run_instances(
        ImageId = ami,
        MinCount = 1,
        MaxCount = 1,
        SubnetId = Id,
        InstanceType = "t2.micro",
        KeyName = keyname,
        UserData = bootstrap,
        SecurityGroupIds = [Sg_Id],
        TagSpecifications=[{'ResourceType': 'instance','Tags': [{'Key': 'Name','Value': 'JamesVM' + str(i + 1)}]}])
    return instances



# Create name for vpcs  
def create_tags (id, letter):
    client.create_tags(
            Resources= [id],
            Tags=[{'Key': 'Name', 'Value': 'VPC-' + str(letter)}]
        )


# create client object from boto3 
client = boto3.client('ec2') 

# Create Resource object for boto 3 
ec2 = boto3.resource('ec2') 


# Input ami and keyname 
ami = (input("Enter the Image ID: "))
keyname = (input("Enter the key name: "))

# get userdata textfile 
userdata = open("userdata.txt", "r+")
privateUserdata = open("privateuserdata.txt", "r+")
bootstrap = str(userdata.read())
privatebootstrap = str(privateUserdata.read())

# Create VPCS and get there IDs 
VPC_A = client.create_vpc(CidrBlock = '10.0.0.0/16')
VPC_B = client.create_vpc(CidrBlock = '192.168.0.0/16')
VPC_A_id = VPC_A['Vpc']['VpcId']
VPC_B_id = VPC_B['Vpc']['VpcId']

# Create names for VPC's 
create_tags(VPC_A_id, "A")
create_tags(VPC_B_id, "B")




# get main route table for use on public subnets 
routeTable_A = client.describe_route_tables(Filters=[{'Name' : 'vpc-id', 'Values' : [VPC_A_id]}])
routeTable_B = client.describe_route_tables(Filters=[{'Name' : 'vpc-id', 'Values' : [VPC_B_id]}])

# Get the main route table ids
VPC_Route_Id_A = (routeTable_A['RouteTables'][0]['Associations'][0]['RouteTableId'])
VPC_Route_Id_B = (routeTable_B['RouteTables'][0]['Associations'][0]['RouteTableId'])


# Create Internet_gateway 
ig_A = client.create_internet_gateway()  
ig_B = client.create_internet_gateway()
ig_A_id = ig_A['InternetGateway']['InternetGatewayId']
ig_B_id = ig_B['InternetGateway']['InternetGatewayId']


# Attach internet gateway to VPC's
internetGateways = []   


# Attach internet gateway
internetGateways.append(attach_internet_gateway(ig_A_id, VPC_A_id))
internetGateways.append(attach_internet_gateway(ig_B_id, VPC_B_id))  


# create vpc_peering connection 
pc = vpc_peering()


## Creating all the routes 
route = [] 

# route to internet gateaway 
route.append(create_route_1(VPC_Route_Id_A, ig_A_id))
route.append(create_route_1(VPC_Route_Id_B, ig_B_id))

# route for VPC Peering
route.append(create_route_2(VPC_Route_Id_A, pc))
route.append(create_route_3(VPC_Route_Id_B, pc))

# Create Secuirty Groups
sg1_A = create_security_group1(VPC_A_id)
sg1_A_id = sg1_A['GroupId']
sg1_B = create_security_group1(VPC_B_id)
sg1_B_id = sg1_B['GroupId']




# create the nexxarcy subnets for VPC-A and VPC-B
subnets_Vpc_A = create_subnets_VpcA()
subnets_Vpc_B = create_subnets_VpcB()
# print (subnets_Vpc_A[0]['Subnet']['SubnetId'])


# Create instances 
myInstances = []
nat_gateway1 = [{}]

# Create VPC's 
for i in range (6):
    if (i == 0):
        allocate = client.allocate_address(Domain = 'vpc')
        SubnetID = subnets_Vpc_A[i]['Subnet']['SubnetId']
        nat_gateway1 = nat_gateway(SubnetID, allocate['AllocationId'], 1)
        instances = create_instance(SubnetID, sg1_A_id, bootstrap)
        associate(VPC_Route_Id_A)
        myInstances.append(instances)
    if (i == 1):
        SubnetID = subnets_Vpc_A[i]['Subnet']['SubnetId']
        instances = create_instance(SubnetID, sg1_A_id, bootstrap)
        associate(VPC_Route_Id_A)
        myInstances.append(instances)
    if (i == 2):
        private_route_table = create_private_route_table(VPC_A_id, 1)
        private_route_table_id = private_route_table['RouteTable']['RouteTableId']
        create_route_2(private_route_table_id, pc)
        time.sleep(5)
        create_route_4(private_route_table_id, nat_gateway1['NatGateway']['NatGatewayId']) 
        SubnetID = subnets_Vpc_A[i]['Subnet']['SubnetId']
        instances = create_instance(SubnetID, sg1_A_id, privatebootstrap)
        associate(private_route_table_id)
        myInstances.append(instances)
    # Creating instances in VPC B
    if (i == 3):
        # Output 1 
        print ("VPC A is now Created with the address " + VPC_A_id)
        allocate = client.allocate_address(Domain = 'vpc')
        SubnetID = subnets_Vpc_B[i - 3]['Subnet']['SubnetId']
        nat_gateway2 = nat_gateway(SubnetID, allocate['AllocationId'], 2)
        instances = create_instance(SubnetID, sg1_B_id, bootstrap)
        associate(VPC_Route_Id_B)
    if (i == 4):
        SubnetID = subnets_Vpc_B[i - 3]['Subnet']['SubnetId']
        instances = create_instance(SubnetID, sg1_B_id, bootstrap)
        associate(VPC_Route_Id_B)
        myInstances.append(instances)
    if (i == 5):
        private_route_table = create_private_route_table(VPC_B_id, 2)
        private_route_table_id = private_route_table['RouteTable']['RouteTableId']
        create_route_3(private_route_table_id, pc)
        time.sleep(5)
        create_route_4(private_route_table_id, nat_gateway2['NatGateway']['NatGatewayId']) 
        SubnetID = subnets_Vpc_B[i - 3]['Subnet']['SubnetId']
        instances = create_instance(SubnetID, sg1_B_id, privatebootstrap)
        associate(private_route_table_id)
        myInstances.append(instances)
        

# Output 2     
print ("VPC B is now created with the address " + VPC_B_id)       

