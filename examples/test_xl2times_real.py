"""Test xl2times with real VEDA model."""

import asyncio
import json
import os
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_xl2times_real():
    """Test xl2times with the DemoS_001 model."""
    print("🚀 Testing XL2TIMES with real VEDA model...")
    
    # Server process configuration
    env = dict(os.environ)
    env["LOG_LEVEL"] = "INFO"
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "xl2times-mcp-server"],
        env=env,
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()
            print("✅ Connected to server")
            
            # Test 1: Process the DemoS_001 model
            print("\n📊 Testing with DemoS_001 model...")
            try:
                result = await session.call_tool(
                    "xl2times_run",
                    arguments={
                        "input": "veda-model-examples/DemoS_001",
                        "output_dir": "output/DemoS_001",
                        "verbose": 1
                    }
                )
                
                if result.content and len(result.content) > 0:
                    content = result.content[0]
                    if hasattr(content, 'text'):
                        response = json.loads(content.text)
                        
                        print(f"\nSuccess: {response.get('success', False)}")
                        print(f"Message: {response.get('message', '')}")
                        print(f"Execution time: {response.get('execution_time', 0):.2f}s")
                        
                        if response.get('files_processed'):
                            print(f"\nFiles processed ({len(response['files_processed'])}):")
                            for f in response['files_processed']:
                                print(f"  - {f}")
                        
                        if response.get('warnings'):
                            print(f"\nWarnings ({len(response['warnings'])}):")
                            for w in response['warnings'][:5]:  # Show first 5
                                print(f"  ⚠️  {w}")
                            if len(response['warnings']) > 5:
                                print(f"  ... and {len(response['warnings']) - 5} more")
                        
                        if response.get('errors'):
                            print(f"\nErrors ({len(response['errors'])}):")
                            for e in response['errors']:
                                print(f"  ❌ {e}")
                        
                        if response.get('output_files'):
                            print(f"\nOutput files ({len(response['output_files'])}):")
                            for f in response['output_files'][:10]:  # Show first 10
                                print(f"  - {f}")
                            if len(response['output_files']) > 10:
                                print(f"  ... and {len(response['output_files']) - 10} more")
                        
                        if response.get('logs'):
                            print("\n--- XL2TIMES Output Preview ---")
                            lines = response['logs'].split('\n')[:20]  # First 20 lines
                            for line in lines:
                                print(line)
                            if len(response['logs'].split('\n')) > 20:
                                print("... (truncated)")
                        
            except Exception as e:
                print(f"❌ Error: {e}")
            
            # Test 2: Test with only_read option
            print("\n📄 Testing with only_read option...")
            try:
                result = await session.call_tool(
                    "xl2times_run", 
                    arguments={
                        "input": "veda-model-examples/DemoS_001",
                        "only_read": True,
                        "verbose": 1
                    }
                )
                
                if result.content and len(result.content) > 0:
                    content = result.content[0]
                    if hasattr(content, 'text'):
                        response = json.loads(content.text)
                        print(f"Success: {response.get('success', False)}")
                        print(f"Message: {response.get('message', '')}")
                        
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print("\n✨ Tests completed!")


def main():
    """Entry point."""
    try:
        asyncio.run(test_xl2times_real())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()