from models import SeatInfo, CgpaRankRange, model_to_dict
from db import db

def interpolate_range(c, c1, r1_min, r1_max, c2, r2_min, r2_max):
    r_min = r1_min + (c - c1) * (r2_min - r1_min) / (c2 - c1)
    r_max = r1_max + (c - c1) * (r2_max - r1_max) / (c2 - c1)

    return round(r_min), round(r_max)



def estimate_rank_range(cgpa_to_rank_map, cgpa):
    if(cgpa > cgpa_to_rank_map[0].cgpa):
        return (1, 1)
    if(cgpa < cgpa_to_rank_map[-1].cgpa):
        print(cgpa, cgpa_to_rank_map[-1].cgpa)
        return (cgpa_to_rank_map[-1].min_rank, cgpa_to_rank_map[-1].max_rank)
    
    left = 0
    right = len(cgpa_to_rank_map) - 1

    while(left <= right):
        mid = (left + right) // 2

        if(cgpa_to_rank_map[mid].cgpa == cgpa):
            return (cgpa_to_rank_map[mid].min_rank, cgpa_to_rank_map[mid].max_rank)

        if(cgpa_to_rank_map[mid].cgpa < cgpa):
            right = mid - 1

        
        if(cgpa_to_rank_map[mid].cgpa > cgpa):
            left = mid + 1


    left = min(left, len(cgpa_to_rank_map) - 1)
    right = max(right, 0)
    

    r1_min = cgpa_to_rank_map[left].min_rank
    r1_max = cgpa_to_rank_map[left].max_rank

    r2_min = cgpa_to_rank_map[right].min_rank
    r2_max = cgpa_to_rank_map[right].max_rank

    c1 = cgpa_to_rank_map[left].cgpa
    c2 = cgpa_to_rank_map[right].cgpa

           
        
    return interpolate_range(cgpa, c1, r1_min, r1_max, c2, r2_min, r2_max)




def fetch_colleges_from_rank(
    rank_min,
    rank_max,  
    branch,
    category,
    gender,
    college_type,
    year
):
    """
    Fetch colleges where the closing rank is >= rank_min.

    Rules:
    - Match exact year, branch, and category.
    - Gender can match the requested gender OR 'OP' (Open to all).
    - If college_type == 'Any', do not filter by college_type.
    - Results are ordered by closing_rank ascending.
    """

    query = SeatInfo.query.filter(
        SeatInfo.year == year,
        SeatInfo.closing_rank >= rank_min,
        SeatInfo.branch == branch,
        SeatInfo.category == category,
        SeatInfo.gender.in_([gender, "OP"])
    )

    if college_type != "Any":
        query = query.filter(
            SeatInfo.college_type == college_type
        )

    return query.order_by(SeatInfo.closing_rank.asc()).all()


def fetch_cgpa_to_rank_map(year):
    """
    Returns all CGPA to rank mappings for a given year,
    ordered by CGPA descending.
    """

    return (
        CgpaRankRange.query
        .filter(CgpaRankRange.year == year)
        .order_by(CgpaRankRange.cgpa.desc())
        .all()
    )



def get_cgpa_from_rank(year, rank):
    result = (
    CgpaRankRange.query
    .with_entities(CgpaRankRange.cgpa)   
    .filter(
        CgpaRankRange.year == year,
        CgpaRankRange.min_rank <= rank,
        CgpaRankRange.max_rank >= rank
    )
    .first()
    )


    cgpa = result[0] if result else None

    return cgpa


def search_colleges(
    q,
    category=None,
    gender=None,
    college_type=None,
    branch=None,
    year=None
):
    query = SeatInfo.query

    # Search by college name or branch
    query = query.filter(
        db.or_(
            SeatInfo.college_name.ilike(f"%{q}%"),
            SeatInfo.branch.ilike(f"%{q}%")
        )
    )

    # Optional filters
    if category:
        query = query.filter(SeatInfo.category == category)

    if gender:
        query = query.filter(
        SeatInfo.gender.in_([gender, "OP"])
    )

    if college_type:
        query = query.filter(SeatInfo.college_type == college_type)

    if branch:
        query = query.filter(SeatInfo.branch == branch)

    if year:
        query = query.filter(SeatInfo.year == int(year))

    # Final query
    results = query.order_by(
        SeatInfo.year.desc(),
        SeatInfo.college_name.asc()
    ).all()

    return [
        {
            **model_to_dict(row),
            "min_cgpa_required": get_cgpa_from_rank(row.year, row.closing_rank),
            "max_cgpa_required": get_cgpa_from_rank(row.year, row.opening_rank),
        }
        for row in results
    ]

    