#!/usr/bin/env python3
"""
SOVD Assistant Demo and Training Data Collector
"""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path
from sovd_nlp_prototype import SOVDAssistant, IntentType

class TrainingDataCollector:
    """Collects and manages training data for ML model development"""
    
    def __init__(self, data_file: str = "sovd_training_data.json"):
        self.data_file = Path(data_file)
        self.training_data = self._load_existing_data()
    
    def _load_existing_data(self) -> list:
        """Load existing training data if available"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load existing training data: {e}")
                return []
        return []
    
    def add_training_example(self, user_input: str, intent: str, entities: dict, 
                           http_request: str, feedback: str = None):
        """Add a new training example"""
        example = {
            "timestamp": datetime.now().isoformat(),
            "input": user_input,
            "intent": intent,
            "entities": entities,
            "http_request": http_request,
            "feedback": feedback
        }
        self.training_data.append(example)
        self._save_data()
    
    def _save_data(self):
        """Save training data to file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.training_data, f, indent=2)
        except Exception as e:
            print(f"Error saving training data: {e}")
    
    def get_statistics(self) -> dict:
        """Get statistics about collected training data"""
        if not self.training_data:
            return {"total": 0, "by_intent": {}}
        
        by_intent = {}
        for example in self.training_data:
            intent = example.get("intent", "unknown")
            by_intent[intent] = by_intent.get(intent, 0) + 1
        
        return {
            "total": len(self.training_data),
            "by_intent": by_intent,
            "latest": self.training_data[-1]["timestamp"] if self.training_data else None
        }

def interactive_demo(config_file: str = None, base_uri: str = None, debug: bool = False):
    """Run an interactive demonstration of the SOVD assistant"""
    try:
        assistant = SOVDAssistant(base_uri=base_uri, config_file=config_file)
        collector = TrainingDataCollector()
        
        print("SOVD Natural Language Diagnostic Assistant")
        print("=" * 60)
        print(f"Target Vehicle: {assistant.base_uri}")
        if debug:
            print("Debug mode enabled")
        print("Ask about vehicle diagnostics in natural language.")
        print("Type 'quit' to exit, 'stats' for statistics")
        print("-" * 60)
        
        while True:
            try:
                user_input = input("\nYour request: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye")
                    break
                
                if user_input.lower() == 'stats':
                    stats = collector.get_statistics()
                    print(f"Training Data Statistics:")
                    print(f"Total examples: {stats['total']}")
                    if stats['by_intent']:
                        print("By intent:")
                        for intent, count in stats['by_intent'].items():
                            print(f"  {intent}: {count}")
                    continue
                
                if not user_input:
                    continue
                
                # Process the request
                result = assistant.process_request(user_input, debug=debug)
                
                if result["success"]:
                    print(f"Intent: {result['intent']}")
                    
                    if result["entities"]:
                        print(f"Entities: {result['entities']}")
                    
                    print(f"Explanation: {result['explanation']}")
                    print(f"HTTP Request: {result['http_request']}")
                    print(f"cURL: {result['curl_command']}")
                    
                    # Ask for feedback
                    feedback = input("Was this correct? (y/n/comment): ").strip()
                    
                    # Collect training data
                    collector.add_training_example(
                        user_input=user_input,
                        intent=result['intent'],
                        entities=result['entities'],
                        http_request=result['http_request'],
                        feedback=feedback if feedback.lower() not in ['y', 'yes'] else "correct"
                    )
                    
                    if feedback.lower() in ['n', 'no']:
                        correction = input("What should the correct intent/request be? ")
                        if correction.strip():
                            print(f"Noted for training: {correction}")
                
                else:
                    print(f"Error: {result['message']}")
                    if result.get("suggestions"):
                        print("Suggestions:")
                        for suggestion in result["suggestions"]:
                            print(f"  {suggestion}")
                    
                    # Still collect this as training data
                    collector.add_training_example(
                        user_input=user_input,
                        intent="unknown",
                        entities={},
                        http_request="",
                        feedback="failed_to_parse"
                    )
            
            except KeyboardInterrupt:
                print("\nGoodbye")
                break
            except Exception as e:
                print(f"Error processing request: {e}")
    
    except Exception as e:
        print(f"Failed to initialize SOVD Assistant: {e}")
        sys.exit(1)

def batch_test(config_file: str = None, base_uri: str = None, debug: bool = False):
    """Run batch tests on predefined examples"""
    try:
        assistant = SOVDAssistant(base_uri=base_uri, config_file=config_file)
        
        test_cases = [
            "List all apps",
            "Show capabilities",
            "Get engine data", 
            "Read system logs",
            "Check for faults",
            "Show PowerSteering sensor data",
            "Get AdvancedLaneKeeping configurations",
            "List Engine operations",
            "Read PowerSteering logs",
            "What apps are available?",
            "Show me the engine status",
            "I need to check for error codes",
            "Security access to engine",
            "Show RearWindows data with schema",
            "Get WindowControl configurations",
        ]
        
        print("Running Batch Tests")
        print("=" * 40)
        print(f"Target: {assistant.base_uri}")
        
        success_count = 0
        
        for i, test_input in enumerate(test_cases, 1):
            print(f"{i:2d}. Testing: '{test_input}'")
            
            try:
                result = assistant.process_request(test_input, debug=debug)
                
                if result["success"]:
                    print(f"    Intent: {result['intent']}")
                    if result["entities"]:
                        print(f"    Entities: {result['entities']}")
                    success_count += 1
                else:
                    print(f"    Failed to parse")
                    
            except Exception as e:
                print(f"    Error: {e}")
        
        print(f"Results: {success_count}/{len(test_cases)} successful ({success_count/len(test_cases)*100:.1f}%)")
        
    except Exception as e:
        print(f"Failed to run batch tests: {e}")
        sys.exit(1)

def export_training_data_for_ml():
    """Export training data in format suitable for ML training"""
    try:
        collector = TrainingDataCollector()
        
        if not collector.training_data:
            print("No training data available")
            return
        
        # Convert to ML-friendly format
        ml_data = []
        for example in collector.training_data:
            ml_example = {
                "text": example["input"],
                "intent": example["intent"],
                "entities": example["entities"]
            }
            ml_data.append(ml_example)
        
        # Save for ML training
        ml_file = "sovd_ml_training_data.json"
        with open(ml_file, 'w') as f:
            json.dump(ml_data, f, indent=2)
        
        print(f"Exported {len(ml_data)} training examples to {ml_file}")
            
    except Exception as e:
        print(f"Export failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="SOVD Natural Language Interface")
    parser.add_argument('command', nargs='?', default='demo', 
                       choices=['demo', 'batch', 'export'],
                       help='Command to run (default: demo)')
    parser.add_argument('--config', '-c', type=str, 
                       help='Path to configuration file')
    parser.add_argument('--uri', '-u', type=str, 
                       help='Base URI for SOVD server')
    parser.add_argument('--debug', '-d', action='store_true',
                       help='Enable debug mode')
    
    args = parser.parse_args()
    
    try:
        if args.command == "demo":
            interactive_demo(config_file=args.config, base_uri=args.uri, debug=args.debug)
        elif args.command == "batch":
            batch_test(config_file=args.config, base_uri=args.uri, debug=args.debug)
        elif args.command == "export":
            export_training_data_for_ml()
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()