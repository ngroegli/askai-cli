import os
import sys
import json
from typing import List, Dict, Any, Optional

class SystemManager:
    def __init__(self, base_path: str):
        """Initialize the system manager.
        
        Args:
            base_path: Base path of the application
        """
        self.systems_dir = os.path.join(base_path, "systems")
        if not os.path.isdir(self.systems_dir):
            raise ValueError(f"No 'systems' directory found at {self.systems_dir}")

    def list_systems(self) -> List[Dict[str, Any]]:
        """List all available system files.
        
        Returns:
            List[Dict[str, Any]]: List of system metadata
        """
        systems = []
        for filename in os.listdir(self.systems_dir):
            if filename.endswith('.md') and not filename.startswith('_'):
                file_path = os.path.join(self.systems_dir, filename)
                system_id = filename.removesuffix('.md')
                
                # Read first line of the file to get the system name
                with open(file_path, 'r') as f:
                    first_line = f.readline().strip()
                    name = first_line.replace('# System:', '').strip()
                
                systems.append({
                    'system_id': system_id,
                    'name': name,
                    'file_path': file_path
                })
        
        return sorted(systems, key=lambda x: x['name'])

    def get_system_content(self, system_id: str) -> Optional[str]:
        """Get the content of a specific system file.
        
        Args:
            system_id: The system identifier (filename without .md)
            
        Returns:
            Optional[str]: The content of the system file if found, None otherwise
        """
        file_path = os.path.join(self.systems_dir, f"{system_id}.md")
        if not os.path.exists(file_path):
            return None
            
        with open(file_path, 'r') as f:
            return f.read()

    def display_system(self, system_id: str) -> None:
        """Display the content of a system file.
        
        Args:
            system_id: The system identifier
        """
        content = self.get_system_content(system_id)
        if content is None:
            raise ValueError(f"System '{system_id}' does not exist")
        print(content)

    def select_system(self) -> Optional[str]:
        """Display an interactive system selection menu.
        
        Returns:
            Optional[str]: Selected system ID or None if selection cancelled
        """
        systems = self.list_systems()
        
        if not systems:
            print("No system files found.")
            return None
            
        print("\nAvailable systems:")
        print("-" * 60)
        
        # Display systems with index
        for i, system in enumerate(systems, 1):
            print(f"{i}. {system['name']}")
            print(f"   ID: {system['system_id']}")
            print("-" * 60)
        
        print("\nOptions:")
        print("1-{0}. Select system".format(len(systems)))
        print("q. Quit")
        
        while True:
            choice = input(f"\nEnter your choice (1-{len(systems)} or q): ").lower()
            
            if choice == 'q':
                return None
            
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(systems):
                    return systems[choice_num - 1]['system_id']
                else:
                    print(f"Please enter a number between 1 and {len(systems)}")
            except ValueError:
                print("Please enter a valid number or 'q' to quit")
