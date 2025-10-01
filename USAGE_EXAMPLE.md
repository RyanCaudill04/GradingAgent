# Usage Example: Grading Binary Search Assignment

This guide demonstrates how to use the Gemini-integrated grading system to grade a Binary Search assignment.

## Prerequisites

1. **Get a Gemini API Key:**
   - Visit https://makersuite.google.com/app/apikey
   - Click "Create API Key"
   - Copy and save your key securely

2. **Get a GitHub Personal Access Token:**
   - Go to https://github.com/settings/tokens
   - Generate new token (classic)
   - Select `repo` scope for private repos
   - Copy the token

3. **Start the system:**
   ```bash
   make up
   ```

## Step 1: Create the Assignment

```bash
curl -X POST http://localhost:8001/assignments \
  -H "Content-Type: application/json" \
  -d '{
    "assignment_name": "BinarySearch"
  }'
```

**Response:**
```json
{
  "id": 1,
  "name": "BinarySearch"
}
```

## Step 2: Create Grading Criteria

Create a file `binary_search_criteria.json`:

```json
{
  "natural_language_rubric": "CSCE-247 Binary Search Assignment Grading Rubric\n\nTotal Points: 100\n\nYou are grading a Java assignment where students must implement binary search from scratch.\n\nGRADING BREAKDOWN:\n\n1. Binary Search Implementation (40 points):\n   - Correctly implements binary search algorithm\n   - Properly divides search space in half each iteration\n   - Returns correct index when element is found\n   - Returns -1 or appropriate value when element not found\n   - Deduct 5-10 points for minor logic errors\n   - Deduct 20-30 points for major algorithmic issues\n\n2. Edge Case Handling (20 points):\n   - Handles empty array: -5 points if missing\n   - Handles single element array: -5 points if missing\n   - Handles element not in array: -5 points if missing\n   - Handles duplicate elements correctly: -5 points if missing\n\n3. Code Quality and Structure (20 points):\n   - Proper variable naming: -5 points if poor\n   - Clean, readable code structure: -5 points if messy\n   - Appropriate use of Java conventions: -5 points if violated\n   - No unnecessary complexity: -5 points if overly complex\n\n4. Documentation (15 points):\n   - JavaDoc comments on public methods: -5 points if missing\n   - Clear parameter descriptions: -5 points if missing\n   - Return value documentation: -5 points if missing\n\n5. Time Complexity (5 points):\n   - Algorithm achieves O(log n) time complexity\n   - Deduct 5 points if implementation is O(n) or worse\n\nBE SPECIFIC: For each deduction, explain exactly what is wrong and reference the specific code location if possible.\n\nBE CONSTRUCTIVE: Provide suggestions for improvement.\n\nFORMAT: Use the format: [-X points] Description of issue",
  "regex_checks": [
    {
      "pattern": "Arrays\\.binarySearch",
      "deduction": 50,
      "message": "Used built-in Arrays.binarySearch() instead of implementing from scratch"
    },
    {
      "pattern": "Collections\\.binarySearch",
      "deduction": 50,
      "message": "Used built-in Collections.binarySearch() instead of implementing from scratch"
    },
    {
      "pattern": "\\.sort\\(",
      "deduction": 10,
      "message": "Sorting the array is not required for binary search (assuming array is pre-sorted)"
    }
  ]
}
```

Upload the criteria:

```bash
curl -X POST http://localhost:8001/assignments/BinarySearch/criteria \
  -F "criteria_file=@binary_search_criteria.json"
```

**Response:**
```json
{
  "message": "Criteria for BinarySearch saved."
}
```

## Step 3: Grade a Student Submission

Assuming a student has pushed their work to `https://github.com/johndoe/csce247-assignments`:

```bash
curl -X POST http://localhost:8001/grade \
  -H "Content-Type: application/json" \
  -d '{
    "assignment_name": "BinarySearch",
    "repo_link": "https://github.com/johndoe/csce247-assignments",
    "token": "ghp_YOUR_GITHUB_TOKEN_HERE",
    "gemini_api_key": "YOUR_GEMINI_API_KEY_HERE"
  }'
```

**Example Response:**
```json
{
  "message": "Assignment grading complete.",
  "student_id": "johndoe",
  "assignment_name": "BinarySearch",
  "grading_result": {
    "grade": 82,
    "feedback": "GRADE: 82/100\n\n==================================================\nDEDUCTIONS:\n  [-5 points] Missing edge case handling for empty arrays\n  [-3 points] Insufficient JavaDoc comments on public methods\n  [-10 points] Variable naming could be more descriptive (using 'l', 'r', 'm' instead of 'left', 'right', 'mid')\n\n==================================================\nDETAILED FEEDBACK:\n[-5 points] The binarySearch method does not properly handle the edge case of an empty array. When the array length is 0, the method should immediately return -1.\n\n[-3 points] The public binarySearch method lacks JavaDoc comments. Professional Java code should include comments describing the method's purpose, parameters (@param), and return value (@return).\n\n[-10 points] Variable names 'l', 'r', and 'm' should be written out as 'left', 'right', and 'mid' for better readability. Single-letter variables make the code harder to understand and maintain.\n\nPositive aspects:\n- The core binary search algorithm is correctly implemented\n- The method achieves O(log n) time complexity as required\n- The code handles the case when the element is not found\n- The iterative approach is efficient and avoids stack overflow issues\n\nSuggestions for improvement:\n1. Add comprehensive JavaDoc documentation\n2. Use full variable names instead of abbreviations\n3. Add validation at the beginning of the method to handle empty arrays\n4. Consider adding a test case for an array with a single element",
    "deductions": [
      "[-5 points] Missing edge case handling for empty arrays",
      "[-3 points] Insufficient JavaDoc comments on public methods",
      "[-10 points] Variable naming could be more descriptive (using 'l', 'r', 'm' instead of 'left', 'right', 'mid')"
    ]
  }
}
```

## Step 4: Retrieve All Grades

Get all grading results:

```bash
curl http://localhost:8001/grades
```

**Response:**
```json
[
  {
    "assignment_name": "BinarySearch",
    "student_id": "johndoe",
    "grade": 82.0,
    "feedback": "GRADE: 82/100\n\n==================================================\n..."
  },
  {
    "assignment_name": "BinarySearch",
    "student_id": "janedoe",
    "grade": 95.0,
    "feedback": "GRADE: 95/100\n\n==================================================\n..."
  }
]
```

## Step 5: Get Specific Student's Grades

```bash
curl http://localhost:8001/grades/johndoe
```

**Response:**
```json
[
  {
    "assignment_name": "BinarySearch",
    "student_id": "johndoe",
    "grade": 82.0,
    "feedback": "GRADE: 82/100\n\n..."
  }
]
```

## Using the Web Interface

### Upload Criteria via Web UI

1. Navigate to http://localhost:8000/upload-criteria/
2. Enter assignment name: `BinarySearch`
3. Upload your `binary_search_criteria.json` file
4. Click "Upload Criteria"

### Grade via Web UI

1. Navigate to http://localhost:8000/grade/
2. Fill in the form:
   - **Assignment Name:** BinarySearch
   - **Repository Link:** https://github.com/johndoe/csce247-assignments
   - **GitHub Token:** ghp_your_token
   - **Gemini API Key:** your_gemini_key
3. Click "Submit for Grading"
4. View the results on the next page

### View All Grades

1. Navigate to http://localhost:8000/grades/
2. Browse all submissions and grades
3. Filter by assignment or student

## Tips for TAs

### Writing Good Rubrics

1. **Be Specific:** Break down the grading into clear categories with point values
2. **Provide Context:** Explain what you're looking for in each category
3. **Include Examples:** Mention specific things that should/shouldn't be in the code
4. **Use Clear Format:** Help Gemini understand how to format deductions

### Using Regex Checks

Use regex checks for:
- Detecting use of forbidden methods/classes
- Finding specific anti-patterns
- Catching obvious violations

**Good regex patterns:**
```json
{
  "pattern": "Arrays\\.binarySearch",
  "deduction": 50,
  "message": "Used built-in binary search"
}
```

**Patterns to avoid:**
- Too generic patterns that catch false positives
- Complex patterns that are hard to debug

### Testing Your Criteria

Before grading all submissions:
1. Test on a known good submission (should get ~100)
2. Test on a known poor submission (should get low grade)
3. Verify deductions make sense
4. Adjust rubric if needed

### Cost Management

- Gemini 1.5 Flash is cost-effective (~$0.00001 per request)
- Average assignment costs < $0.01 to grade
- Monitor your API usage at https://makersuite.google.com/

## Troubleshooting

### "Repository not found" error
- Check if the repository is private and token has access
- Verify the repository URL is correct
- Ensure the GitHub token hasn't expired

### "Assignment folder not found" error
- Student must have a folder with exact assignment name
- Folder names are case-sensitive: `BinarySearch` ≠ `binarysearch`

### "No Java files found" error
- Verify `.java` files exist in the assignment folder
- Check that files have `.java` extension (not `.txt` or `.java.txt`)

### Gemini API errors
- Verify your API key is valid
- Check if you've exceeded rate limits
- Ensure billing is enabled if required

### Unexpected grades
- Review the detailed feedback to see what Gemini caught
- Check if regex patterns are too aggressive
- Adjust the rubric to be more/less strict
