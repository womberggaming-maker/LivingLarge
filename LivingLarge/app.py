import re
from flask import Flask, render_template, request, abort, session, redirect, url_for
from homes import homes 
import random 

app = Flask(__name__)
app.secret_key = "living_large_secret_key"


def default_profile():
   return {
       "city": "",
       "budget": None,
       "min_size": None,
       "rooms": None,
       "wants_shopping": False,
       "wants_garage": False,
       "wants_garden": False,
       "wants_forest": False,
       "wants_commute": False,
       "wants_family": False,
       "wants_investment": False,
   }

def has_active_preferences(profile: dict) -> bool:
   if not profile:
       return False
   return any([
       bool(profile.get("city")),
       profile.get("budget") is not None,
       profile.get("min_size") is not None,
       profile.get("rooms") is not None,
       profile.get("wants_shopping", False),
       profile.get("wants_garage", False),
       profile.get("wants_garden", False),
       profile.get("wants_forest", False),
       profile.get("wants_commute", False),
       profile.get("wants_family", False),
       profile.get("wants_investment", False),
   ])

def parse_dream_home(text):
   text = text.lower()
   profile = default_profile()

   # By
   if "vejle" in text:
       profile["city"] = "Vejle"
   elif "horsens" in text:
       profile["city"] = "Horsens"
   elif "aarhus" in text:
       profile["city"] = "Aarhus"
   elif "randers" in text:
       profile["city"] = "Randers"
   elif "silkeborg" in text:
       profile["city"] = "Silkeborg"
   elif "odense" in text:
       profile["city"] = "Odense"
   elif "københavn" in text:
       profile["city"] = "København"
   elif "esbjerg" in text:
       profile["city"] = "Esbjerg"
   elif "kolding" in text:
       profile["city"] = "Kolding"
   elif "aalborg" in text:
       profile["city"] = "Aalborg"
   elif "blåvand" in text:
       profile["city"] = "Blåvand"
   elif "skagen" in text:
       profile["city"] = "Skagen"
   # Budget
   budget_match = re.search(r'(\d{6,7})', text)
   if budget_match:
        profile["budget"] = int(budget_match.group(1))
   elif "2 mio" in text:
        profile["budget"] = 2000000
   elif "2.5 mio" in text or "2500000" in text:
        profile["budget"] = 2500000
   elif "2,5 mio" in text:
        profile["budget"] = 2500000
   elif "3 mio" in text:
        profile["budget"] = 3000000
   elif "3,5 mio" in text:
        profile["budget"] = 3500000
   elif "4 mio" in text:
        profile["budget"] = 4000000
   # Størrelse
   if "stor" in text or "150" in text:
       profile["min_size"] = 150
   # Features
   if "3 værelser" in text or "3 vaerelser" in text:
       profile["rooms"] = 3
   elif "4 værelser" in text or "4 vaerelser" in text:
       profile["rooms"] = 4
   elif "5 værelser" in text or "5 vaerelser" in text:
       profile["rooms"] = 5
   if "garage" in text:
       profile["wants_garage"] = True
   if "have" in text:
       profile["wants_garden"] = True
   if "natur" in text or "skov" in text or "roligt" in text:
       profile["wants_forest"] = True
   if "pendling" in text or "motorvej" in text or "arbejde" in text:
       profile["wants_commute"] = True
   if "familie" in text or "børn" in text or "skole" in text:
       profile["wants_family"] = True
   if "investering" in text:
       profile["wants_investment"] = True
   if "indkøb" in text or "butik" in text or "supermarked" in text:
       profile["wants_shopping"] = True
       print("PARSED USER:", profile)
   return profile

def format_price(price):
   return f"{price:,.0f}".replace(",", ".")
app.jinja_env.globals.update(format_price=format_price)

def calculate_match(user_profile: dict, home: dict) -> int:
   score = 0
   max_score = 0
   # Kritiske kriterier
   city = (user_profile.get("city") or "").strip().lower()
   budget = user_profile.get("budget")
   min_size = user_profile.get("min_size")
   rooms = user_profile.get("rooms")
   home_city = (home.get("city") or "").strip().lower()
   home_price = home.get("price", 0)
   home_size = home.get("size", 0)
   home_rooms = home.get("rooms", 0)
   # BY - meget vigtig
   if city:
       max_score += 35
       if home_city == city:
           score += 35
       else:
           score -= 25
   # BUDGET - meget vigtig
   if budget is not None:
       max_score += 30
       if home_price <= budget:
           score += 30
       elif home_price <= budget * 1.05:
           score += 15
       elif home_price <= budget * 1.10:
           score += 6
       else:
           score -= 22
   # STØRRELSE
   if min_size is not None:
       max_score += 15
       if home_size >= min_size:
           score += 15
       elif home_size >= min_size * 0.9:
           score += 7
       else:
           score -= 6
   # VÆRELSER
   if rooms is not None:
       max_score += 12
       if home_rooms >= rooms:
           score += 12
       elif home_rooms == rooms - 1:
           score += 5
       else:
           score -= 5
   # BLØDE ØNSKER
   preference_rules = [
       ("wants_shopping", "near_shopping", 5),
       ("wants_garage", "garage", 8),
       ("wants_garden", "garden", 7),
       ("wants_forest", "forest_nearby", 7),
   ]
   for user_key, home_key, weight in preference_rules:
       if user_profile.get(user_key, False):
           max_score += weight
           if home.get(home_key):
               score += weight
           else:
               score -= max(2, weight // 2)
   # SCORING VIA TAL
   if user_profile.get("wants_commute", False):
       max_score += 6
       commute_score = home.get("commute_score", 0)
       if commute_score >= 8:
           score += 6
       elif commute_score >= 6:
           score += 3
       else:
           score -= 3
   if user_profile.get("wants_family", False):
       max_score += 6
       family_score = home.get("family_score", 0)
       if family_score >= 8:
           score += 6
       elif family_score >= 6:
           score += 3
       else:
           score -= 3
   if user_profile.get("wants_investment", False):
       max_score += 6
       investment_score = home.get("investment_score", 0)
       if investment_score >= 8:
           score += 6
       elif investment_score >= 6:
           score += 3
       else:
           score -= 3
   if max_score == 0:
       return 0
   # Normaliser
   final_score = round((score / max_score) * 100)
   # Ekstra straf hvis både by er forkert og pris er over budget
   if city and home_city != city and budget is not None and home_price > budget:
       final_score -= 10
   # Clamp
   final_score = max(0, min(final_score, 95))
   return final_score

def get_match_reasons(user_profile: dict, home: dict) -> list:
   reasons = []
   city = (user_profile.get("city") or "").strip().lower()
   budget = user_profile.get("budget")
   min_size = user_profile.get("min_size")
   rooms = user_profile.get("rooms")
   home_city = (home.get("city") or "").strip().lower()
   home_price = home.get("price", 0)
   home_size = home.get("size", 0)
   home_rooms = home.get("rooms", 0)
   if city and home_city == city:
       reasons.append("Rigtig by")
   if budget is not None:
       if home_price <= budget:
           reasons.append("Inden for budget")
       elif home_price <= budget * 1.05:
           reasons.append("Lidt over budget")
   if min_size is not None:
       if home_size >= min_size:
           reasons.append("Stor nok")
       elif home_size >= min_size * 0.9:
           reasons.append("Næsten stor nok")
   if rooms is not None:
       if home_rooms >= rooms:
           reasons.append("Nok værelser")
       elif home_rooms == rooms - 1:
           reasons.append("Tæt på ønsket antal værelser")
   if user_profile.get("wants_garage") and home.get("garage"):
       reasons.append("Garage")
   if user_profile.get("wants_garden") and home.get("garden"):
       reasons.append("Have")
   if user_profile.get("wants_forest") and home.get("forest_nearby"):
       reasons.append("Tæt på natur")
   if user_profile.get("wants_shopping") and home.get("near_shopping"):
       reasons.append("Tæt på indkøb")
   if user_profile.get("wants_commute") and home.get("commute_score", 0) >= 7:
       reasons.append("God pendling")
   if user_profile.get("wants_family") and home.get("family_score", 0) >= 7:
       reasons.append("Familievenligt")
   if user_profile.get("wants_investment") and home.get("investment_score", 0) >= 7:
       reasons.append("God investering")
   return reasons

def get_match_summary(user_profile: dict, home: dict) -> str:
   positives = []
   negatives = []
   city = (user_profile.get("city") or "").strip().lower()
   budget = user_profile.get("budget")
   min_size = user_profile.get("min_size")
   rooms = user_profile.get("rooms")
   home_city = (home.get("city") or "").strip().lower()
   home_price = home.get("price", 0)
   home_size = home.get("size", 0)
   home_rooms = home.get("rooms", 0)
   # Positive signaler
   if city and home_city == city:
       positives.append("ligger i din ønskede by")
   elif city and home_city != city:
       negatives.append("ligger ikke i din ønskede by")
   if budget is not None:
       if home_price <= budget:
           positives.append("holder sig inden for budget")
       elif home_price <= budget * 1.05:
           positives.append("kun ligger lidt over budget")
       else:
           negatives.append("ligger tydeligt over budget")
   if min_size is not None:
       if home_size >= min_size:
           positives.append("har den ønskede størrelse")
       else:
           negatives.append("er mindre end ønsket")
   if rooms is not None:
       if home_rooms >= rooms:
           positives.append("har nok værelser")
       elif home_rooms < rooms:
           negatives.append("har færre værelser end ønsket")
   if user_profile.get("wants_garage"):
       if home.get("garage"):
           positives.append("har garage")
       else:
           negatives.append("mangler garage")
   if user_profile.get("wants_garden"):
       if home.get("garden"):
           positives.append("har have")
       else:
           negatives.append("mangler have")
   if user_profile.get("wants_forest"):
       if home.get("forest_nearby"):
           positives.append("ligger tæt på naturen")
       else:
           negatives.append("ikke ligger tæt på naturen")
   if user_profile.get("wants_shopping"):
       if home.get("near_shopping"):
           positives.append("er tæt på indkøb")
       else:
           negatives.append("ikke er tæt på indkøb")
   if user_profile.get("wants_commute"):
       if home.get("commute_score", 0) >= 7:
           positives.append("har god pendling")
       else:
           negatives.append("har mindre god pendling")
   if user_profile.get("wants_family"):
       if home.get("family_score", 0) >= 7:
           positives.append("passer godt til familieliv")
       else:
           negatives.append("ikke er det stærkeste familie-match")
   if user_profile.get("wants_investment"):
       if home.get("investment_score", 0) >= 7:
           positives.append("har investeringspotentiale")
       else:
           negatives.append("ikke scorer højt som investering")
   # Byg tekst
   if positives and negatives:
       return (
           "Boligen matcher delvist dine ønsker, fordi den "
           + " og ".join(positives[:2])
           + ", men den "
           + negatives[0]
           + "."
       )
   if positives:
       return (
           "Boligen matcher godt dine ønsker, fordi den "
           + " og ".join(positives[:2])
           + "."
       )
   if negatives:
       return (
           "Boligen matcher kun i begrænset grad dine ønsker, fordi den "
           + negatives[0]
           + "."
       )
   return "Boligen matcher delvist din profil."

def get_match_improvement(user_profile, home):
   issues = []
   if user_profile["budget"] is not None and home["price"] > user_profile["budget"]:
       issues.append("prisen ligger over dit budget")
   if user_profile["min_size"] is not None and home["size"] < user_profile["min_size"]:
       issues.append("boligen er mindre end ønsket")
   if user_profile["wants_commute"] and home["commute_score"] < 7:
       issues.append("pendlingen er lidt længere")
   if not issues:
       return ""
   return "Matchen er lavere fordi " + ", ".join(issues) + "."

def get_lifestyle_comment(home):
   comments = []
   if home["family_score"] >= 8:
       comments.append("Området er meget familievenligt")
   if home["commute_score"] >= 8:
       comments.append("Pendlingen er kort")
   if home["investment_score"] >= 8:
       comments.append("Boligen har stærkt investeringspotentiale")
   if not comments:
       return ""
   return "Fremtidsperspektiv: " + ", ".join(comments) + "."

def get_match_limitations(user_profile: dict, home: dict) -> list:
   reasons = []
   city = (user_profile.get("city") or "").strip().lower()
   budget = user_profile.get("budget")
   min_size = user_profile.get("min_size")
   rooms = user_profile.get("rooms")
   home_city = (home.get("city") or "").strip().lower()
   home_price = home.get("price", 0)
   home_size = home.get("size", 0)
   home_rooms = home.get("rooms", 0)
   if city and home_city != city:
       reasons.append("Boligen ligger ikke i din ønskede by")
   if budget is not None and home_price > budget:
       if home_price <= budget * 1.05:
           reasons.append("Boligen ligger lidt over dit budget")
       else:
           reasons.append("Boligen ligger tydeligt over dit budget")
   if min_size is not None and home_size < min_size:
       reasons.append("Boligen er mindre end ønsket")
   if rooms is not None and home_rooms < rooms:
       reasons.append("Boligen har færre værelser end ønsket")
   if user_profile.get("wants_garage") and not home.get("garage"):
       reasons.append("Boligen har ikke garage")
   if user_profile.get("wants_garden") and not home.get("garden"):
       reasons.append("Boligen har ikke have")
   if user_profile.get("wants_forest") and not home.get("forest_nearby"):
       reasons.append("Boligen ligger ikke tæt på natur")
   if user_profile.get("wants_shopping") and not home.get("near_shopping"):
       reasons.append("Boligen ligger ikke tæt på indkøb")
   if user_profile.get("wants_commute") and home.get("commute_score", 0) < 7:
       reasons.append("Pendlingen er ikke optimal")
   if user_profile.get("wants_family") and home.get("family_score", 0) < 7:
       reasons.append("Boligen scorer ikke højt på familievenlighed")
   if user_profile.get("wants_investment") and home.get("investment_score", 0) < 7:
       reasons.append("Boligen scorer ikke højt som investering")
   return reasons

def get_match_label(match_score: int) -> str:
   if match_score >= 80:
       return "Perfekt match"
   elif match_score >= 65:
       return "Godt match"
   elif match_score >= 45:
       return "Relevant match"
   elif match_score >= 25:
       return "Muligt match"
   return "Svagt match"

def get_match_count(user_profile: dict, home: dict):
   total = 0
   matched = 0
   if user_profile["city"]:
       total += 1
       if home["city"].lower() == user_profile["city"].lower():
           matched += 1
   if user_profile["budget"] is not None:
       total += 1
       if home["price"] <= user_profile["budget"]:
           matched += 1
   if user_profile["min_size"] is not None:
       total += 1
       if home["size"] >= user_profile["min_size"]:
           matched += 1
   if user_profile["wants_garage"]:
       total += 1
       if home["garage"]:
           matched += 1
   if user_profile["wants_garden"]:
       total += 1
       if home["garden"]:
           matched += 1
   if user_profile["wants_forest"]:
       total += 1
       if home["forest_nearby"]:
           matched += 1
   if user_profile["wants_commute"]:
       total += 1
       if home["commute_score"] >= 7:
           matched += 1
   if user_profile["wants_family"]:
       total += 1
       if home["family_score"] >= 7:
           matched += 1
   if user_profile["wants_investment"]:
       total += 1
       if home["investment_score"] >= 7:
           matched += 1
   if user_profile.get("wants_shopping", False):
       total += 1
       if home.get("near_shopping"):
           matched += 1
   return matched, total

def get_lifestyle_tags(home):
   tags = []
   if home.get("family_score", 0) >= 7:
       tags.append("Perfekt til familie")
   if home.get("forest_nearby"):
       tags.append("Tæt på natur")
   if home.get("commute_score", 0) >= 7:
       tags.append("Kort pendling")
   if home.get("investment_score", 0) >= 7:
       tags.append("God investering")
   return tags

def get_top_matches_explanation(user_profile, matches):
   if not matches:
       return ""
   # Tag top 3
   top_matches = matches[:3]
   reasons = []
   for match in top_matches:
       home = match
       if user_profile["budget"] is not None:
           if home["price"] <= user_profile["budget"]:
               reasons.append("inden for budget")
           else:
               reasons.append("over budget")
       if user_profile["min_size"] is not None:
           if home["size"] >= user_profile["min_size"]:
               reasons.append("stor nok")
           else:
               reasons.append("for lille")
       if user_profile["wants_garden"] and home.get("garden"):
           reasons.append("have")
       if user_profile["wants_garage"] and home.get("garage"):
           reasons.append("garage")
       if user_profile["wants_forest"] and home.get("forest_nearby"):
           reasons.append("tæt på natur")
       if user_profile.get("wants_shopping", False) and home.get("near_shopping"):
           reasons.append("tæt på indkøb")
   # Fjern duplicates
   unique_reasons = []
   for r in reasons:
       if r not in unique_reasons:
           unique_reasons.append(r)
   # Tag maks 3
   top_reasons = unique_reasons[:3]
   if not top_reasons:
    return "Vi har udvalgt disse boliger ud fra din samlede profil."
   if len(top_reasons) == 1:
    reason_text = top_reasons[0]
   elif len(top_reasons) == 2:
    reason_text = " og ".join(top_reasons)
   else:
    reason_text = ", ".join(top_reasons[:-1]) + " og " + top_reasons[-1]
   return "Vi har udvalgt disse boliger, fordi de matcher dine vigtigste ønsker – især " + reason_text + "."

def enrich_home_for_user(user_profile: dict, home: dict) -> dict:
   home_with_score = home.copy()
   match_score = calculate_match(user_profile, home)
   match_reasons = get_match_reasons(user_profile, home)
   match_summary = get_match_summary(user_profile, home)
   limitations = get_match_limitations(user_profile, home)
   matched_count, total_count = get_match_count(user_profile, home)
   home_with_score["match_score"] = match_score
   home_with_score["match_label"] = get_match_label(match_score)
   home_with_score["match_reasons"] = match_reasons
   home_with_score["match_summary"] = match_summary
   home_with_score["limitations"] = limitations
   home_with_score["matched_count"] = matched_count
   home_with_score["total_count"] = total_count
   home_with_score["future_comment"] = get_lifestyle_comment(home)
   home_with_score["tags"] = get_lifestyle_tags(home)
   # Bruges til mere stabil sortering
   home_with_score["_tie_strength"] = matched_count
   home_with_score["_price_distance"] = abs((user_profile.get("budget") or home.get("price", 0)) - home.get("price", 0))
   return home_with_score

def has_active_preferences(profile: dict) -> bool:
   if not profile:
       return False
   return any([
       bool(profile.get("city")),
       profile.get("budget") is not None,
       profile.get("min_size") is not None,
       profile.get("rooms") is not None,
       profile.get("wants_shopping", False),
       profile.get("wants_garage", False),
       profile.get("wants_garden", False),
       profile.get("wants_forest", False),
       profile.get("wants_commute", False),
       profile.get("wants_family", False),
       profile.get("wants_investment", False),
   ])

def get_matches(user_profile: dict, homes_list: list) -> tuple[list, bool]:
   matches = []
   low_matches = []
   used_fallback = False
   for home in homes_list:
       enriched_home = enrich_home_for_user(user_profile, home)
       match_score = enriched_home["match_score"]
       if match_score >= 25:
           matches.append(enriched_home)
       else:
           low_matches.append(enriched_home)
   # Stabil sortering:
   # 1. højeste score
   # 2. flest matchede kriterier
   # 3. mindst afstand til budget
   # 4. titel som sidste stabile tie-break
   matches.sort(
       key=lambda x: (
           x["match_score"],
           x["_tie_strength"],
           -x["_price_distance"],
           x["title"]
       ),
       reverse=True,
   )
   if not matches:
       low_matches.sort(
           key=lambda x: (
               x["match_score"],
               x["_tie_strength"],
               -x["_price_distance"],
               x["title"]
           ),
           reverse=True,
       )
       matches = low_matches[:5]
       used_fallback = True
   return matches, used_fallback

@app.route("/", methods=["GET", "POST"])
def home():
   results = []
   explanation = ""
   no_results_message = ""
   used_fallback = False
   user = session.get("user_profile", default_profile())
   dream_text = session.get("last_dream_home", "")
   if request.method == "POST":
       dream_text = request.form.get("dream_home", "").strip()
       if dream_text:
           user = parse_dream_home(dream_text)
       else:
           user = default_profile()
           user["city"] = request.form.get("city", "").strip()
           user["budget"] = int(request.form.get("budget")) if request.form.get("budget") else None
           user["min_size"] = int(request.form.get("min_size")) if request.form.get("min_size") else None
           user["rooms"] = int(request.form.get("rooms")) if request.form.get("rooms") else None
           user["wants_shopping"] = "wants_shopping" in request.form
           user["wants_garage"] = "wants_garage" in request.form
           user["wants_garden"] = "wants_garden" in request.form
           user["wants_forest"] = "wants_forest" in request.form
           user["wants_commute"] = "wants_commute" in request.form
           user["wants_family"] = "wants_family" in request.form
           user["wants_investment"] = "wants_investment" in request.form
       session["user_profile"] = user
       session["last_dream_home"] = dream_text
       return redirect(url_for("home", _anchor="results-section"))
   if has_active_preferences(user):
       results, used_fallback = get_matches(user, homes)
       if not results:
           no_results_message = (
               "Vi fandt desværre ingen boliger, der matcher præcist. "
               "Prøv at hæve dit budget lidt, vælge et andet område eller justere dine krav."
           )
       explanation = get_top_matches_explanation(user, results)
   return render_template(
       "index.html",
       results=results,
       favorites=session.get("favorites", []),
       user=user,
       homes=homes,
       explanation=explanation,
       no_results_message=no_results_message,
       used_fallback=used_fallback,
       dream_text=dream_text,
       scroll_to_results=has_active_preferences(user),
   )


@app.route("/bolig/<int:home_id>")
def bolig_detaljer(home_id):
   home = next((h for h in homes if h["id"] == home_id), None)
   if not home:
       abort(404)
   user_profile = session.get("user_profile")
   if user_profile:
       enriched_home = enrich_home_for_user(user_profile, home)
       match_score = enriched_home["match_score"]
       match_reasons = enriched_home["match_reasons"]
       match_summary = enriched_home["match_summary"]
       match_details = enriched_home["match_details"]
       limitations = enriched_home["limitations"]
   else:
       enriched_home = home.copy()
       match_score = 0
       match_reasons = []
       match_summary = "Vælg dine kriterier på forsiden for at se hvorfor boligen matcher."
       match_details = []
       limitations = []
   return render_template(
       "details.html",
       home=enriched_home,
       match_score=match_score,
       match_reasons=match_reasons,
       match_summary=match_summary,
       match_details=match_details,
       limitations=limitations,
       user_profile=user_profile,
   )

@app.route("/toggle_favorite/<int:home_id>")
def toggle_favorite(home_id):
   if "favorites" not in session:
       session["favorites"] = []
   favorites = session["favorites"]
   if home_id in favorites:
       favorites.remove(home_id)
   else:
       favorites.append(home_id)
   session["favorites"] = favorites
   return redirect(request.referrer or "/")

@app.route("/profile", methods=["GET", "POST"])
def profile():
   if not session.get("logged_in"):
       return redirect(url_for("login"))
   user_profile = session.get("user_profile", default_profile())
   if request.method == "POST":
       user_profile["city"] = request.form.get("city", "").strip()
       user_profile["budget"] = int(request.form.get("budget")) if request.form.get("budget") else None
       user_profile["min_size"] = int(request.form.get("min_size")) if request.form.get("min_size") else None
       user_profile["rooms"] = int(request.form.get("rooms")) if request.form.get("rooms") else None
       selected_preferences = request.form.getlist("preferences")
       user_profile["wants_garden"] = "garden" in selected_preferences
       user_profile["wants_garage"] = "garage" in selected_preferences
       user_profile["wants_forest"] = "forest" in selected_preferences
       user_profile["wants_shopping"] = "shopping" in selected_preferences
       user_profile["wants_commute"] = "commute" in selected_preferences
       user_profile["wants_family"] = "family" in selected_preferences
       user_profile["wants_investment"] = "investment" in selected_preferences
       session["user_profile"] = user_profile
       return redirect(url_for("profile"))
   favorite_ids = session.get("favorites", [])
   favorite_homes = [home for home in homes if home["id"] in favorite_ids]
   return render_template(
       "profile.html",
       user_profile=user_profile,
       favorite_homes=favorite_homes
   )

@app.route("/login", methods=["GET", "POST"])
def login():
   if request.method == "POST":
       email = request.form.get("email", "").strip()
       password = request.form.get("password", "").strip()
       # MVP placeholder
       session["logged_in"] = True
       session["user_email"] = email
       return redirect(url_for("profile"))
   return render_template("login.html")

@app.route("/logout")
def logout():
   session.clear()
   return redirect(url_for("home"))

@app.route("/about")
def about():
   return render_template("about.html")

@app.route("/reset")
def reset():
   session.clear()
   return redirect(url_for("home") + "#search-section")

if __name__ == "__main__":
   app.run(host="0.0.0.0", port=10000)
