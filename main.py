from flask import Flask, render_template, request, send_from_directory
from db import db
from predictor import fetch_cgpa_to_rank_map, fetch_colleges_from_rank, estimate_rank_range, search_colleges


app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


BRANCHES = {
    # Computer Science & IT
    "CSE": "Computer Science and Engineering",
    "IT": "Information Technology",
    "CSBS": "Computer Science and Business Systems",
    "CSD": "Computer Science and Design",
    "MAC": "Mathematics and Computing",
    "IOT": "Internet of Things",
    "CSEIL": "Computer Science & Engineering (Hindi Medium)",

    # AI, Data Science & Cyber Security
    "AI": "Artificial Intelligence",
    "AIML": "Artificial Intelligence & Machine Learning",
    "AIADS": "Artificial Intelligence and Data Science",
    "CSEDS": "Computer Science and Engineering (Data Science)",
    "CSECS": "Computer Science and Engineering (Cyber Security)",
    "CSEBC": "Computer Science and Engineering (Blockchain)",
    "ITAIAR": "Information Technology (Artificial Intelligence & Robotics)",

    # Electronics & Electrical
    "EC": "Electronics and Communication Engineering",
    "ECACT": "Electronics and Communication (Advanced Communication Technology)",
    "EE": "Electrical Engineering",
    "ELECT ELEX": "Electrical & Electronics Engineering",
    "EEIOT": "Electrical Engineering (Internet of Things)",
    "EI": "Electronics and Instrumentation Engineering",
    "EL": "Electronics Engineering",
    "ET": "Electronics and Telecommunication Engineering",
    "ECS": "Electronics and Computer Science",

    # Mechanical, Automobile & Robotics
    "MECH": "Mechanical Engineering",
    "AUTO": "Automobile Engineering",
    "ARE": "Automation and Robotics",
    "AIR": "Robotics and Artificial Intelligence",
    "MTENG": "Mechatronics Engineering",
    "EV": "Electric Vehicles",

    # Civil, Chemical & Production
    "CIVIL": "Civil Engineering",
    "CHEM": "Chemical Engineering",
    "IP": "Industrial & Production Engineering",
    "AGE": "Agricultural Engineering",

    # Mining
    "MINING": "Mining Engineering",
    "MMP": "Mining and Mineral Processing",

    # Specialized Programs
    "BM": "Biomedical Engineering",
    "PCT": "Petrochemical Technology",
    "FTS": "Fire Technology & Safety",
}



RANK_MAPS_CACHE = {}
YEARS = [2025, 2024]

def fetch_rank_maps_cache():
    for year in YEARS:
        RANK_MAPS_CACHE[year] = fetch_cgpa_to_rank_map(year)

    
def get_colleges(cgpa, branches, category, gender, college_type):

    result = {}

    for year in YEARS:

        # Fetch CGPA to rank mapping
        cgpa_to_rank_map = RANK_MAPS_CACHE[year]

        # Estimate rank range
        rank_range = estimate_rank_range(cgpa_to_rank_map, cgpa)
        min_rank, max_rank = rank_range


        # Fetch colleges
        colleges = fetch_colleges_from_rank(
            min_rank,
            max_rank,
            branches,
            category,
            gender,
            college_type,
            year,
        
        )
        result[year] = {}

        result[year]['colleges'] = colleges
    
        
        result[year]['prediction'] = (
            f"Estimated rank range: {min_rank} - {max_rank}"
        )
    

    return result

def get_rank(cgpa):
    result = {}

    for year in YEARS:

        cgpa_to_rank_map = RANK_MAPS_CACHE[year]


        rank_range = estimate_rank_range(cgpa_to_rank_map, cgpa)
        min_rank, max_rank = rank_range


        result[year] = {}
        
        result[year]['prediction'] = (
            f"Estimated rank range: {min_rank} - {max_rank}"
        )
    

    return result


with app.app_context():
        fetch_rank_maps_cache()



@app.route('/predictor', methods=['GET', 'POST'])
def predictor():

    
    if request.method == 'GET':
        return render_template(
            'predictor.html',
            data=None,
            prediction=None,
            colleges=None
        )


    # Get form values
    cgpa = float(request.form.get('cgpa'))
    category = request.form.get('category')
    gender = request.form.get('gender')
    college_type = request.form.get('college_type')
    branches = request.form.getlist('branch')

    # Store user data
    form_data = {
        'cgpa': cgpa,
        'category': category,
        'gender': gender,
        'college_type': college_type,
        'branch': branches
    }



    predection = get_colleges(cgpa, branches, category, gender, college_type)
 


    return render_template(
        'predictor.html',  
        data=form_data,
        predection=predection
    )




@app.route("/search")
def search():
    q = request.args.get("q", "").strip()

    # Read filters
    category = request.args.get("category", "").strip()
    gender = request.args.get("gender", "").strip()
    college_type = request.args.get("college_type", "").strip()
    branches = request.args.getlist('branch')
    year = request.args.get("year", "").strip()

    # If no search query, show empty page
    if not q:
        return render_template(
            "search.html",
            data=None,
            colleges=None
        )

    # Preserve all form values
    data = {
        "q": q,
        "category": category,
        "gender": gender,
        "college_type": college_type,
        "branches": branches,
        "year": year,
    }

    # Search with filters
    colleges = search_colleges(
        q=q,
        category=category or None,
        gender=gender or None,
        college_type=college_type or None,
        branches=branches or None,
        year=year or None,
    )

    return render_template(
        "search.html",
        data=data,
        colleges=colleges
    )

@app.route('/rank_predictor', methods=['GET', 'POST'])
def rank():
    if request.method == 'GET':
            return render_template('rank.html',data=None, predection=None)
    
    data = {}
    cgpa = float(request.form.get('cgpa'))
    if cgpa:
        data["cgpa"] = cgpa
        
    return render_template('rank.html',data=data, predection=get_rank(cgpa))




@app.route("/analysis", methods=['GET'])
def analysis():
    return render_template('analysis.html')

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


@app.template_filter("branch_name")
def branch_name(code):
    return BRANCHES.get(code, code)

    


@app.route("/robots.txt")
def robots():
    return send_from_directory("static", "robots.txt")

@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory("static", "sitemap.xml")

@app.route('/google3bf79a468e1ed3d9.html')
def google():
    return send_from_directory("static", "google3bf79a468e1ed3d9.html")


if __name__ == '__main__':
    app.run(debug=True, host="10.141.121.37", port=80)