from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.structure import TanhLayer
from pybrain.tools.customxml import NetworkWriter
from pybrain.tools.customxml import NetworkReader

"""columns = ['having_IP_Address',
'URL_Length',
'Shortining_Service',
'having_At_Symbol',
'double_slash_redirecting',
'Prefix_Suffix',
'having_Sub_Domain',
'SSLfinal_State',
'Domain_registeration_length',
'Favicon',
'port',
'HTTPS_token',
'Request_URL',
'URL_of_Anchor',
'Links_in_tags',
'SFH',
'Submitting_to_email',
'Abnormal_URL',
'Redirect',
'on_mouseover',
'RightClick',
'popUpWidnow',
'Iframe',
'age_of_domain',
'DNSRecord',
'web_traffic ',
'Page_Rank',
'Google_Index',
'Links_pointing_to_page',
'Statistical_report',
'Result']
"""
net = None
def build_bp():
    global net
    net = buildNetwork(30, 2, 1, bias=True, hiddenclass=TanhLayer)
    ds = SupervisedDataSet(30, 1)
    fp=open("./data.csv", "r");
    alllines=fp.readlines();
    for eachline in alllines:
        data = eachline.rstrip('\n').split(',')
        data_int = []
        for i in data:
            data_int.append(int(i))
        input = data_int[0:len(data_int)-1]
        target = data_int[len(data_int)-1:len(data_int)]
        ds.addSample(input,target)
    fp.close()
    print len(ds)
    for inpt, target in ds:
        print inpt, target
#    trainer = BackpropTrainer(net, ds)
#    trainer.trainUntilConvergence(maxEpochs=10000)
#    NetworkWriter.writeToFile(net, './bpstudy.xml')
    net = NetworkReader.readFrom('./bpstudy.xml')
    #test
    fp=open("./data.csv", "r");
    alllines=fp.readlines();
    for eachline in alllines:
        data = eachline.rstrip('\n').split(',')
        data_int = []
        for i in data:
            data_int.append(int(i))
        input = data_int[0:len(data_int)-1]
        target = data_int[len(data_int)-1:len(data_int)]
        print net.activate(input)
    fp.close()

def activate_bp(input):
    return net.activate(input)

