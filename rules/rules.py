# rule_based_system/rules.py

rules = {
    "1": ["responses['Q1'] == 'Janosch'"],
    "2": ["responses['Q2'] == 'Test - All questions'"],
    "3": ["responses['Q3'] == 'Weiblich'"],
    "4": ["responses['Q4'] == 1954"],
    "5": ["responses['Q5'] == True"],
    "6": ["responses['Q6'] == 160"],
    "7": ["responses['Q7'] == 50"],
    "8": ["responses['Q8'] == 'Keine'"],
    "9": ["responses['Q9'] == 'Nein'"],
    "10": ["responses['Q10'] == 5"],
    "11": ["responses['Q11'] == 5"],
    "12": ["responses['Q12'] == 5"],
    "13": ["responses['Q13'] == 'Ausdauer, Kraft, Flexibilität, HIIT'"],
    "14": ["responses['Q14'] == 'Joggen'"],
    "15": ["responses['Q15'] == 'Yoga'"],
    "16": ["responses['Q16'] == 'vegan'"],
    "17": ["responses['Q17'] == 1"],
    "18": ["responses['Q18'] == 1"],
    "19": ["responses['Q19'] == 5"],
    "20": ["responses['Q20'] == 5"],
    "21": ["responses['Q21'] == 1"],
    "22": ["responses['Q22'] == 5"],
    "23": ["responses['Q23'] == '16:8 (täglich 14-16 Stunden fasten)'"],
    "24": ["responses['Q24'] == 12"],
    "25": ["responses['Q25'] == 16"],
    "26": ["responses['Q26'] == 20"],
    "27": ["responses['Q27'] == 'mehr als 12'"],
    "28": ["responses['Q28'] == 'gar keinen'"],
    "29": ["responses['Q29'] == 'sehr gut'"],
    "30": ["responses['Q30'] == '7-9'"],
    "31": ["responses['Q31'] == 1"],
    "32": ["responses['Q32'] == 'mehr als 60min'"],
    "33": ["responses['Q33'] == 'mehr als 60min'"],
    "34": ["responses['Q34'] == 'fast täglich'"],
    "35": ["responses['Q35'] == 'viele gute Freunde'"],
    "36": ["responses['Q36'] == 'Aktivismus'"],
    "37": ["responses['Q37'] == 'nein'"],
    "38": ["responses['Q38'] == 1"],
    "39": ["responses['Q39'] == 1"],
    "40": ["responses['Q40'] == 'gar keine'"],
    "41": ["responses['Q41'] == 'gar keine'"],
    "42": ["responses['Q42'] == 5"],
    "43": ["responses['Q43'] == 5"],
    "44": ["responses['Q44'] == 5"],
    "45": ["responses['Q45'] == 5"],
    "46": ["responses['Q46'] == 1"],
    "47": ["responses['Q47'] == 5"],
    "48": ["responses['Q48'] == 5"],
    "49": ["responses['Q49'] == 1"],
    "50": ["responses['Q50'] == 5"],
    "51": ["responses['Q51'] == 5"],
    "52": ["responses['Q52'] == 1"],
    "53": ["responses['Q53'] == 4"],
    "54": ["responses['Q54'] == 60"]
}

def get_rules():
    print(rules)
    return rules

if __name__ == "__main__":
    all_rules = get_rules()
    print(all_rules)
