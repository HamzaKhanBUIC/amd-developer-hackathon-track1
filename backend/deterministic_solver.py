import re
import sympy

def solve(prompt, category):
    """
    Attempts to deterministically solve a prompt based on its category.
    Returns the string answer if successful, or None if it cannot be solved deterministically.
    """
    prompt_lower = prompt.lower()
    
    if category == "math":
        return solve_math(prompt_lower)
    elif category == "ner":
        return solve_ner(prompt)
    
    return None

def solve_math(prompt):
    """
    Try to parse and solve basic math word problems using sympy or regex.
    """
    # Look for explicit equations like "2400 * 0.37" or simple word patterns
    # Very simple extraction for now: if we see an explicit math expression
    # This is a basic implementation; top teams use more robust parsing
    
    # Try to extract numbers
    numbers = re.findall(r'\b\d+(?:\.\d+)?\b', prompt.replace(',', ''))
    
    # Simple percentage pattern: "X units ... Y%" -> X * (Y/100)
    if '%' in prompt and len(numbers) >= 2:
        try:
            # Assume the two numbers are the base and the percentage
            # e.g., "A warehouse starts with 2,400 units. In Q1 it sells 37%..."
            # Let's find the percentage
            pct_matches = re.findall(r'(\d+(?:\.\d+)?)\s*%', prompt)
            if pct_matches:
                pct = float(pct_matches[0])
                for num in numbers:
                    num_f = float(num)
                    if num_f != pct:
                        ans = num_f * (pct / 100.0)
                        # Remove decimals if whole number
                        if ans.is_integer():
                            ans = int(ans)
                        return str(ans)
        except Exception:
            pass
            
    # Try standard math equations (e.g. "What is 15 + 20?")
    math_eq = re.search(r'([\d\.]+\s*[\+\-\*\/]\s*[\d\.]+)', prompt)
    if math_eq:
        try:
            expr = sympy.sympify(math_eq.group(1))
            ans = float(expr)
            if ans.is_integer():
                ans = int(ans)
            return str(ans)
        except Exception:
            pass

    return None

def solve_ner(prompt):
    """
    Try to extract basic entities (Dates, simple Names) using regex.
    """
    entities = set()
    
    # Simple date extraction
    date_matches = re.findall(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?(?:,)?\s+\d{4}\b', prompt, re.IGNORECASE)
    for date in date_matches:
        entities.add(date)
        
    # If we found something very obvious, return it
    if entities:
        return ", ".join(entities)
        
    return None

if __name__ == "__main__":
    print(solve("A warehouse starts with 2,400 units. In Q1 it sells 37%.", "math"))
    print(solve("The event is on March 15, 2023 at the main hall.", "ner"))
