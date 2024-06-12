import numpy

banks_list = ["chase","amex","c1","bilt","citi","wf"]
airlines_list = ["virgin_atlantic","flying_blue","delta","united","jet_blue","american","velocity","alaska","aeroplan","british","turkish",\
                "quantas","avianca","southwest","iberia","ANA","cathay","singapore"]
hotels_list = ["marriott","hilton","ihg","hyatt"]

conversion_dict={}
conversion_dict["chase"]={}
conversion_dict["amex"]={}
conversion_dict["c1"]={}
conversion_dict["bilt"]={}
conversion_dict["citi"]={}
conversion_dict["wf"]={}

conversion_dict["virgin_atlantic"]={}
conversion_dict["flying_blue"]={}
conversion_dict["delta"]={}
conversion_dict["united"]={}
conversion_dict["jet_blue"]={}
conversion_dict["american"]={}
conversion_dict["velocity"]={}
conversion_dict["alaska"]={}
conversion_dict["aeroplan"]={}
conversion_dict["british"]={}
conversion_dict["turkish"]={}
conversion_dict["quantas"]={}
conversion_dict["avianca"]={}
conversion_dict["southwest"]={}
conversion_dict["iberia"]={}
conversion_dict["ANA"]={}
conversion_dict["cathay"]={}
conversion_dict["singapore"]={}

conversion_dict["marriott"]={}
conversion_dict["hilton"]={}
conversion_dict["ihg"]={}
conversion_dict["hyatt"]={}

points_dict={}
points_dict["chase"]=0
points_dict["amex"]=0
points_dict["c1"]=0
points_dict["bilt"]=2465
points_dict["citi"]=0
points_dict["wf"]=0
points_dict["virgin_atlantic"]=0
points_dict["flying_blue"]=0
points_dict["delta"]=11910
points_dict["united"]=0
points_dict["jet_blue"]=0
points_dict["american"]=0
points_dict["velocity"]=0
points_dict["alaska"]=0
points_dict["aeroplan"]=0
points_dict["british"]=0
points_dict["turkish"]=4165
points_dict["quantas"]=0
points_dict["avianca"]=0
points_dict["southwest"]=0
points_dict["iberia"]=0
points_dict["ANA"]=0
points_dict["cathay"]=0
points_dict["singapore"]=0
points_dict["marriott"]=0
points_dict["hilton"]=0
points_dict["ihg"]=0
points_dict["hyatt"]=0


conversion_dict["chase"]["virgin_atlantic"]=1
conversion_dict["chase"]["flying_blue"]=1
conversion_dict["chase"]["united"]=1
conversion_dict["chase"]["jet_blue"]=1
conversion_dict["chase"]["aeroplan"]=1
conversion_dict["chase"]["british"]=1
conversion_dict["chase"]["southwest"]=1
conversion_dict["chase"]["iberia"]=1
conversion_dict["chase"]["singapore"]=1
conversion_dict["chase"]["marriott"]=1
conversion_dict["chase"]["ihg"]=1
conversion_dict["chase"]["hyatt"]=1

conversion_dict["amex"]["flying_blue"]=1
conversion_dict["amex"]["delta"]=1
conversion_dict["amex"]["jet_blue"]=0.8
conversion_dict["amex"]["velocity"]=1
conversion_dict["amex"]["aeroplan"]=1
conversion_dict["amex"]["british"]=1
conversion_dict["amex"]["quantas"]=1
conversion_dict["amex"]["avianca"]=1
conversion_dict["amex"]["iberia"]=1
conversion_dict["amex"]["ANA"]=1
conversion_dict["amex"]["cathay"]=1
conversion_dict["amex"]["singapore"]=1
conversion_dict["amex"]["marriott"]=1
conversion_dict["amex"]["hilton"]=2

conversion_dict["c1"]["virgin_atlantic"]=1
conversion_dict["c1"]["flying_blue"]=1
conversion_dict["c1"]["aeroplan"]=1
conversion_dict["c1"]["british"]=1
conversion_dict["c1"]["turkish"]=1
conversion_dict["c1"]["quantas"]=1
conversion_dict["c1"]["avianca"]=1
conversion_dict["c1"]["cathay"]=1
conversion_dict["c1"]["singapore"]=1

conversion_dict["bilt"]["virgin_atlantic"]=1
conversion_dict["bilt"]["flying_blue"]=1
conversion_dict["bilt"]["united"]=1
conversion_dict["bilt"]["alaska"]=1
conversion_dict["bilt"]["aeroplan"]=1
conversion_dict["bilt"]["british"]=1
conversion_dict["bilt"]["turkish"]=1
conversion_dict["bilt"]["avianca"]=1
conversion_dict["bilt"]["iberia"]=1
conversion_dict["bilt"]["cathay"]=1
conversion_dict["bilt"]["marriott"]=1
conversion_dict["bilt"]["ihg"]=1
conversion_dict["bilt"]["hyatt"]=1
conversion_dict["bilt"]["hilton"]=1

conversion_dict["citi"]["virgin_atlantic"]=1
conversion_dict["citi"]["flying_blue"]=1
conversion_dict["citi"]["jet_blue"]=1
conversion_dict["citi"]["velocity"]=1
conversion_dict["citi"]["turkish"]=1
conversion_dict["citi"]["quantas"]=1
conversion_dict["citi"]["avianca"]=1
conversion_dict["citi"]["cathay"]=1
conversion_dict["citi"]["singapore"]=1

conversion_dict["wf"]["flying_blue"]=1
conversion_dict["wf"]["british"]=1
conversion_dict["wf"]["avianca"]=1
conversion_dict["wf"]["iberia"]=1
