import gbk_parser

records= gbk_parser.records

def write_comb():
    with open('comb.txt','w') as f:
        combs = []
        for record in records:
            for feature in record.features:
                f.write(str(feature.type))
                f.write(str(feature.location)+"\n")
write_comb()
