# LLM Call

## Delete old files

```bash
aws s3api list-objects-v2 \
  --bucket pangea-data-dev-bedrock-datasets \
  --prefix llm-output/2025/10/latest/es/ \
  --query "Contents[?LastModified<='2025-11-18T00:00:00Z'].{Key: Key}" \
  --output json | jq '{Objects: ., Quiet: false}' > delete_fixed.json
```

```bash
aws s3api delete-objects \
  --bucket pangea-data-dev-bedrock-datasets \
  --delete file://delete_fixed.json
```

### too many files?

```bash
jq -c '(.Objects) as $objs
      | range(0; $objs|length; 1000) as $i
      | {Objects: $objs[$i:$i+1000], Quiet: false}' delete_fixed.json \
| while read -r payload; do
    # show payload (dry-run): echo "$payload"
    aws s3api delete-objects --bucket pangea-data-dev-bedrock-datasets --delete "$payload" || {
      echo "delete failed for chunk"; exit 1
    }
  done
```

## Main Step Function Input Event

### full run

```json
{
  "dataprep": {
    "snowflake_secret_name": "dev/operations/snowflake/de-operations",
    "inputs": {
      "averages": {
        "template_name": "extract_averages.sql",
        "output_stage": "DEV_PANGEA_RAW_LAKE.PUBLIC.DEV_S3_BEDROCK_STAGE"
      },
      "senders": {
        "template_name": "extract_sender_data.sql",
        "output_stage": "DEV_PANGEA_RAW_LAKE.PUBLIC.DEV_S3_BEDROCK_STAGE",
        "limit": 100
      }
    }
  },
  "s3_config": {
    "bucket": "pangea-data-dev-bedrock-datasets"
  },
  "flows": {
    "generator": {
      "identifier": "KSTF27PEBA",
      "alias_identifier": "K5ER1FQRFB"
    },
    "evaluator": {
      "identifier": "F9PU38SFCH",
      "alias_identifier": "BYSY8M5JAT",
      "score_threshold": 17
    },
    "translator": {
      "identifier": "T5UKLI6R8U",
      "alias_identifier": "ZX7X0WR3MQ"
    }
  },
  "control_flow": {
    "skip_data_generation": false,
    "only_data_generation": false,
    "is_translation_only": false,
    "skip_translation": false
  }
}
```

### overwrite

```json
{
  "dataprep": {
    "snowflake_secret_name": "dev/operations/snowflake/de-operations",
    "overwrites": {
      "execution_timestamp" : "20251118T201912"
    },
    "inputs": {
      "averages": {
        "template_name": "extract_averages.sql",
        "output_stage": "DEV_PANGEA_RAW_LAKE.PUBLIC.DEV_S3_BEDROCK_STAGE"
      },
      "senders": {
        "template_name": "extract_sender_data.sql",
        "output_stage": "DEV_PANGEA_RAW_LAKE.PUBLIC.DEV_S3_BEDROCK_STAGE",
        "limit": 100
      }
    }
  },
  "s3_config": {
    "bucket": "pangea-data-dev-bedrock-datasets"
  },
  "flows": {
    "generator": {
      "identifier": "KSTF27PEBA",
      "alias_identifier": "K5ER1FQRFB"
    },
    "evaluator": {
      "identifier": "F9PU38SFCH",
      "alias_identifier": "BYSY8M5JAT",
      "score_threshold": 17
    },
    "translator": {
      "identifier": "TI0MN51LWH",
      "alias_identifier": "ZX7X0WR3MQ"
    }
  },
  "control_flow": {
    "skip_data_generation": true,
    "only_data_generation": false,
    "is_translation_only": false,
    "skip_translation": false
  }
}
```



## Child Step Funtion Input Event

```json
{
  "objKeyParts": {
    "date_str": "20251112T152942",
    "base_path": "",
    "month_year": "2025/10",
    "file_name_base": "fffa0f5e3cff4c638d54911eb4619b15"
  },
  "ParentExecutionId": "arn:aws:states:us-west-2:999402065626:execution:999402065626-us-west-2-sender-insights-phase-2-parent/Map:afca70ed-ddb6-3472-bab0-3fd9e4df4b15",
  "segmentDataPrefix": "segment-data/2025/10/20251112T152942",
  "fileInfo": {
    "Etag": "\"403f59246b9d216453847b57dcad8e1b\"",
    "Key": "sender-data/2025/10/20251112T152942/fffa0f5e3cff4c638d54911eb4619b15.json",
    "LastModified": 1762961568,
    "Size": 5965,
    "StorageClass": "STANDARD"
  },
  "s3Config": {
    "ManifestKey": "aggregated-results/2025/10/20251112T152942",
    "Bucket": "pangea-data-dev-bedrock-datasets",
    "Prefix": "sender-data/2025/10/20251112T152942"
  },
  "userConfig": {
    "segmentDataFile": "segment-data/2025/10/20251112T152942"
  },
  "flowConfig": {
    "evalScoreThreshold": 17,
    "genFlowAliasIdentifier": "K5ER1FQRFB",
    "evalFlowAliasIdentifier": "BYSY8M5JAT",
    "transFlowAliasIdentifier": "2NUWMW8EQ9",
    "genFlowIdentifier": "KSTF27PEBA",
    "evalFlowIdentifier": "F9PU38SFCH",
    "transFlowIdentifier": "TI0MN51LWH"
    
  },
  "controlFlow": {
    "translateOnly": true
  }
}
```

## Awesome Tools

1. `source .venv/bin/activate`
2. `aws sso login --profile sso-ro-data-dev`
3. Overwrite Flow's values in `scripts/convert_api_def_to_cfn.py`
4. Download

  ```bash
  ❯ python scripts/convert_api_def_to_cfn.py \
  --flow-id "K4GBAIZLNA" \
  --flow-version "DRAFT" \
  --output-file templates/flows/TranslatorSenderFlow.yml
  ```

## Prompt

Extract and translate the following JSON keys from English to Spanish: summary, insight1.text, insight2.text, insight3.text. Return the original JSON structure with translated values, plus add a "score" object containing: - semantic_coherence: score 0-1 - meaning_fidelity: score 0-1 - naturalness: score 0-1 - overall_score: average of the three scores Output only valid JSON without markdown formatting or additional text. Don't include backticks in the final JSON output; don't output anything other than the JSON content. output template { "summary": "", "insight1": { "text": "", "material_icon": "" }, "insight2": { "text": "", "material_icon": "" }, "insight3": { "text": "", "material_icon": "" }, "score": { "coherence": 0.0, "fidelity": 0.0, "naturalness": 0.0, "overall": 0.0 } } input {{summary_english_insights}}.



## Translator Flow Input Event

```json
"flowConfig": {
  "transFlowIdentifier": "K4GBAIZLNA",
  "transFlowIdentifier": "2NUWMW8EQ9"
}

```json
{
  "inputs": {
    "generated_summary": "llm-output/2025/10/latest/en/0343c100e7994713ba9d3bbdde9d5e5d.json"
  },
  "outputs": {
    "translated_summary": "llm-output/2025/10/latest/es/openai/0343c100e7994713ba9d3bbdde9d5e5d.json"
  }
}
```

```json
{
  "inputs": {
    "generated_summary": "llm-output/2025/10/latest/en/ff33337ec9474cbfa9e409ece42bd22c.json"
  },
  "outputs": {
    "translated_summary": "llm-output/2025/10/latest/es/ff33337ec9474cbfa9e409ece42bd22c.json"
  }
}
```

## Step Function


TODO: pass new values from parent state machine

- trans_flow_id
- trans_flow_alias_id
- skip_translation
- is_translation_only

```json
{
  "StartAt": "Log Input",
  "States": {
    "Log Input": {
      "Type": "Pass",
      "Assign": {
        "gen_flow_id": "{% $states.input.flowConfig.genFlowIdentifier %}",
        "gen_flow_alias_id": "{% $states.input.flowConfig.genFlowAliasIdentifier %}",
        "eval_flow_id": "{% $states.input.flowConfig.evalFlowIdentifier %}",
        "eval_flow_alias_id": "{% $states.input.flowConfig.evalFlowAliasIdentifier %}",
        "trans_flow_id": "{% $states.input.flowConfig.transFlowIdentifier %}",
        "trans_flow_alias_id": "{% $states.input.flowConfig.transFlowAliasIdentifier %}",
        "eval_score_threshold": "{% $states.input.flowConfig.evalScoreThreshold %}",
        "parent_execution_id": "{% $states.input.ParentExecutionId %}",
        "bucket": "{% $states.input.s3Config.Bucket %}",
        "object_key_parts": "{% $states.input.objKeyParts %}",
        "insights_output_key": "{% $states.input.objKeyParts.base_path & 'llm-output/' & $states.input.objKeyParts.month_year & '/' & $states.input.objKeyParts.date_str & '/' & $states.input.objKeyParts.file_name_base & '.json' %}",
        "eval_output_key": "{% $states.input.objKeyParts.base_path & 'llm-eval-results/' & $states.input.objKeyParts.month_year & '/' & $states.input.objKeyParts.date_str & '/' & $states.input.objKeyParts.file_name_base & '.json' %}",
        "insights_output_prefix": "{% $states.input.objKeyParts.base_path & 'llm-output/' & $states.input.objKeyParts.month_year & '/' & $states.input.objKeyParts.date_str %}",
        "eval_output_prefix": "{% $states.input.objKeyParts.base_path & 'llm-eval-results/' & $states.input.objKeyParts.month_year & '/' & $states.input.objKeyParts.date_str %}",
        "sender_file_name": "{% $states.input.objKeyParts.file_name_base & '.json' %}",
        "render_output_key": "{% $states.input.objKeyParts.base_path & 'rendered_output/' & $states.input.objKeyParts.month_year & '/' & $states.input.objKeyParts.date_str & '/' & $states.input.objKeyParts.file_name_base & '.html' %}",
        "sender_data_key": "{% $states.input.fileInfo.Key %}",
        "segment_data_prefix": "{% $states.input.segmentDataPrefix %}",
        "attempt_count": 0,
        "total_score": 0,
        "is_pass": false,
        "skip_tranlation": false,
        "is_translation_only": true,
        "latest_en_output_key": "{% $states.input.objKeyParts.base_path & 'llm-output/' & $states.input.objKeyParts.month_year & '/latest/en/' & $states.input.objKeyParts.file_name_base & '.json' %}",
        "latest_es_output_key": "{% $states.input.objKeyParts.base_path & 'llm-output/' & $states.input.objKeyParts.month_year & '/latest/es/' & $states.input.objKeyParts.file_name_base & '.json' %}"
      },
      "QueryLanguage": "JSONata",
      "Next": "Choice"
    },
    "Choice": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$is_translation_only",
          "BooleanEquals": true,
          "Next": "Build Translator Flow Input"
        }
      ],
      "Default": "Get Segment File Name"
    },
    "Get Segment File Name": {
      "Type": "Task",
      "Parameters": {
        "Bucket.$": "$bucket",
        "Key.$": "$sender_data_key"
      },
      "Resource": "arn:aws:states:::aws-sdk:s3:getObject",
      "ResultSelector": {
        "fileContent.$": "States.StringToJson($.Body)"
      },
      "ResultPath": "$.s3Data",
      "Next": "Build Segment Data File"
    },
    "Build Segment Data File": {
      "Type": "Pass",
      "Assign": {
        "segment_data_key": "{% $segment_data_prefix & '/' & $states.input.s3Data.fileContent.`1. sender_profile`.region.averages_file %}"
      },
      "QueryLanguage": "JSONata",
      "Next": "Update Output Keys"
    },
    "Update Output Keys": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$attempt_count",
          "NumericGreaterThan": 0,
          "Next": "Set Attempted Output Keys"
        }
      ],
      "Default": "Build Generator Flow Input"
    },
    "Set Attempted Output Keys": {
      "Type": "Pass",
      "Assign": {
        "insights_output_key": "{% $insights_output_prefix & '/attempt-' & $attempt_count & '/' & $sender_file_name %}",
        "eval_output_key": "{% $eval_output_prefix & '/attempt-' & $attempt_count & '/' & $sender_file_name %}"
      },
      "QueryLanguage": "JSONata",
      "Next": "Build Generator Flow Input"
    },
    "Build Generator Flow Input": {
      "Type": "Pass",
      "Parameters": {
        "flowInput": {
          "content": {
            "document": {
              "inputs": {
                "sender_info.$": "$sender_data_key",
                "segment_data.$": "$segment_data_key"
              },
              "outputs": {
                "result.$": "$insights_output_key"
              }
            }
          },
          "nodeName": "FlowInputNode",
          "nodeOutputName": "document"
        }
      },
      "Next": "Invoke Generator Flow"
    },
    "Invoke Generator Flow": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "Payload": {
          "flowInput.$": "$.flowInput",
          "parentExecutionId.$": "$parent_execution_id",
          "flowIdentifier.$": "$gen_flow_id",
          "flowAliasIdentifier.$": "$gen_flow_alias_id"
        },
        "FunctionName": "sender-insights-phase-2-invoke"
      },
      "ResultSelector": {
        "parsedBody.$": "States.StringToJson($.Payload.body)",
        "statusCode.$": "$.Payload.statusCode"
      },
      "Retry": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 2,
          "BackoffRate": 1.5
        }
      ],
      "Next": "Build Eval Flow Input"
    },
    "Build Eval Flow Input": {
      "Type": "Pass",
      "Parameters": {
        "flowInput": {
          "content": {
            "document": {
              "inputs": {
                "user_data.$": "$sender_data_key",
                "averages.$": "$segment_data_key",
                "generated_summary.$": "$insights_output_key"
              },
              "outputs": {
                "result.$": "$eval_output_key"
              }
            }
          },
          "nodeName": "FlowInputNode",
          "nodeOutputName": "document"
        }
      },
      "Next": "Invoke Eval Flow"
    },
    "Invoke Eval Flow": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "Payload": {
          "flowInput.$": "$.flowInput",
          "parentExecutionId.$": "$parent_execution_id",
          "flowIdentifier.$": "$eval_flow_id",
          "flowAliasIdentifier.$": "$eval_flow_alias_id"
        },
        "FunctionName": "sender-insights-phase-2-invoke"
      },
      "ResultSelector": {
        "parsedBody.$": "States.StringToJson($.Payload.body)",
        "statusCode.$": "$.Payload.statusCode"
      },
      "Retry": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 2,
          "BackoffRate": 1.5
        }
      ],
      "Next": "Parse JSON"
    },
    "Parse JSON": {
      "Type": "Pass",
      "Parameters": {
        "parsedJson.$": "States.StringToJson($.parsedBody.result.results[0].flowOutputEvent.content.document)"
      },
      "Next": "Read Total Score"
    },
    "Read Total Score": {
      "Type": "Pass",
      "Assign": {
        "total_score.$": "$.parsedJson.total_score"
      },
      "Next": "Is Pass"
    },
    "Is Pass": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$total_score",
          "NumericGreaterThanEqualsPath": "$eval_score_threshold",
          "Next": "CopyObject"
        }
      ],
      "Default": "Check Max Attempts"
    },
    "CopyObject": {
      "Type": "Task",
      "Parameters": {
        "Bucket.$": "$bucket",
        "CopySource.$": "States.Format('{}/{}', $bucket, $insights_output_key)",
        "Key.$": "$latest_en_output_key"
      },
      "Assign": {
        "is_pass": true,
        "total_score.$": "$total_score"
      },
      "Resource": "arn:aws:states:::aws-sdk:s3:copyObject",
      "Next": "Branch"
    },
    "Branch": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$skip_tranlation",
          "BooleanEquals": false,
          "Next": "Build Translator Flow Input"
        }
      ],
      "Default": "End"
    },
    "Build Translator Flow Input": {
      "Type": "Pass",
      "Parameters": {
        "flowInput": {
          "content": {
            "document": {
              "inputs": {
                "generated_summary.$": "$latest_en_output_key"
              },
              "outputs": {
                "translated_summary.$": "$latest_es_output_key"
              }
            }
          },
          "nodeName": "FlowInputNode",
          "nodeOutputName": "document"
        }
      },
      "Next": "Invoke Translator Flow"
    },
    "Invoke Translator Flow": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Parameters": {
        "Payload": {
          "flowInput.$": "$.flowInput",
          "parentExecutionId.$": "$parent_execution_id",
          "flowIdentifier.$": "$trans_flow_id",
          "flowAliasIdentifier.$": "$trans_flow_alias_id"
        },
        "FunctionName": "sender-insights-phase-2-invoke"
      },
      "ResultSelector": {
        "parsedBody.$": "States.StringToJson($.Payload.body)",
        "statusCode.$": "$.Payload.statusCode"
      },
      "Retry": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 2,
          "BackoffRate": 1.5
        }
      ],
      "Next": "End"
    },
    "End": {
      "Type": "Pass",
      "Comment": "Final state - return structured output",
      "Parameters": {
        "status": "completed",
        "processedOutput": {
          "is_pass.$": "$is_pass",
          "total_score.$": "$total_score",
          "score_threshold.$": "$eval_score_threshold",
          "id.$": "$object_key_parts.file_name_base",
          "attempt_count.$": "$attempt_count"
        },
        "completedAt.$": "$$.State.EnteredTime"
      },
      "OutputPath": "$.processedOutput",
      "Next": "Success"
    },
    "Success": {
      "Type": "Succeed"
    },
    "Check Max Attempts": {
      "Type": "Choice",
      "Choices": [
        {
          "Next": "Increment Attempts Counter",
          "Variable": "$attempt_count",
          "NumericLessThan": 1
        }
      ],
      "Default": "End"
    },
    "Increment Attempts Counter": {
      "Type": "Pass",
      "Assign": {
        "attempt_count.$": "States.MathAdd($attempt_count, 1)"
      },
      "Next": "Update Output Keys"
    }
  }
}
```

## Configuración IaC por modelo LLM

### OpenAI GPT-OSS-120b-1:0 (On-Demand)

#### Input Configuration

- Sin StopSequences!

#### Variable/Input ModelId

```yaml
```

#### Prompt Definition

```yaml
```

#### Prompt Policy

```yaml
```
