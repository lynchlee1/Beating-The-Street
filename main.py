from btsHTML import create_html
from btsQuery import query_all_data
test_cases = ["ORI", "SKX", "UMBF", "AVTR", "CAG", "CMA", "OSK", "LBRDA", "LBRDK", 
            "PRI", "ZION", "LKQ", "AA", "DDS", "INGR", "APA", "GAP", "LNC", "EMN",
            "ALSN", "ADT", "TMHC", "FLR", "GPK", "MTG", "MTDR", "THG", "NXST", "CWAN",
            "URBN", "MARA", "MAT", "CALM", "ACT", "MTH", "AX", "SKYW", "SIGI", "NJR", 
            "MGY", "GHC", "RDN", "WFRD", "ANF", "CBT", "KBH", "MCY", "CRC", "MHO", 
            "ENS", "CNO", "EEFT", "LNTH", "FULT", "ASO", "OTTR", "TGNA", "CIVI", 
            "AZZ", "VC", "KMPR", "MATX", "SM", "TPH", "NMIH", "COLM", "GRBK", "ARLP", 
            "BKE", "VAC", "BHF", "CLSK", "DFH", "NOG", "CPRX", "OII", "INSW", "AGIO", 
            "HCI", "PRDO", "HRMY", "HNI", "UPWK", "YELP", "CCS", "CASH", "HMN", "SLVM", 
            "ROCK", "LBRT", "MNR", "MD", "GBX", "AMPH", "FOR", "SBH", "NRP", "QCRH", 
            "SPH", "FUBO", "INVX", "GIII", "VTOL", "SAFT", "GCT", "OSBC", "UAN", "BBW",
            "CTLP", "GLDD", "NTGR", "UFCS", "PLOW", "IBTA", "JBSS", "ETD", "SSTK", "CDNA", 
            "SNCY", "HRTG", "THFF", "RIGL", "CSV", "LEGH", "OXM", "DJCO", "DGICB", 
            "DGICA", "TTI", "FPH", "NUS", "SIGA", "OSPN", "FMNB", "SCVL", "CBNK", "ACIC", 
            "EBF", "ITIC", "NUTX", "EBS", "SMLR", "SD", "IMXI", "SBC", "IBEX", "LXFR", 
            "ABEO", "CTMX", "NL"]

for ticker in test_cases:
    data = query_all_data(ticker)
    if not isinstance(data, list):
        print("Creating HTML for", ticker, "...")
        create_html(data)
