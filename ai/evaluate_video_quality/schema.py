SCHEMA = {
  "type": "object",
  "properties": {
    "artistic_creative_merit": {
      "type": "object",
      "properties": {
        "score": {
          "type": "string",
          "enum": ['1', '2', '3', '4', '5'],
          "description": "A score from 1 to 5 based on the originality and aesthetic appeal of the content."
        },
        "justification": {
          "type": "string",
          "description": "A brief explanation for the assigned score."
        }
      },
      "required": [
        "score",
        "justification"
      ]
    },
    "technical_execution": {
      "type": "object",
      "properties": {
        "score": {
          "type": "string",
          "enum": ['1', '2', '3', '4', '5'],
          "description": "A score from 1 to 5 for the technical quality, including video, audio, and editing."
        },
        "justification": {
          "type": "string",
          "description": "A brief explanation for the assigned score."
        }
      },
      "required": [
        "score",
        "justification"
      ]
    },
    "clarity_cohesion": {
      "type": "object",
      "properties": {
        "score": {
          "type": "string",
          "enum": ['1', '2', '3', '4', '5'],
          "description": "A score from 1 to 5 for how clear and well-structured the content's message is."
        },
        "justification": {
          "type": "string",
          "description": "A brief explanation for the assigned score."
        }
      },
      "required": [
        "score",
        "justification"
      ]
    },
    "value_purpose": {
      "type": "object",
      "properties": {
        "score": {
          "type": "string",
          "enum": ['1', '2', '3', '4', '5'],
          "description": "A score from 1 to 5 for the value the content provides to the viewer."
        },
        "justification": {
          "type": "string",
          "description": "A brief explanation for the assigned score."
        }
      },
      "required": [
        "score",
        "justification"
      ]
    },
    "platform_synergy": {
      "type": "object",
      "properties": {
        "score": {
          "type": "string",
          "enum": ['1', '2', '3', '4', '5'],
          "description": "A score from 1 to 5 for how well the content uses the platform's unique features."
        },
        "justification": {
          "type": "string",
          "description": "A brief explanation for the assigned score."
        }
      },
      "required": [
        "score",
        "justification"
      ]
    }
  },
  "required": [
    "artistic_creative_merit",
    "technical_execution",
    "clarity_cohesion",
    "value_purpose",
    "platform_synergy"
  ]
}