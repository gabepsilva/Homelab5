#!/usr/bin/env python3
import os
import time
import signal
import sys
import argparse
from datetime import datetime

class GPUTempController:
    def __init__(self, card_num=0, target_temp=70, hwmon_path=None, perf_mode='high', power_limit=None):
        """
        Initialize GPU temperature controller
        card_num: GPU card number (default: 0)
        target_temp: Target temperature in Celsius (default: 70)
        hwmon_path: Optional direct path to hwmon directory
        perf_mode: Performance mode (default: 'high')
        power_limit: Power limit in watts (default: None, uses maximum available)
        """
        self.target_temp = target_temp
        self.card_num = card_num
        self.running = True
        
        # Base card path
        self.card_path = f"/sys/class/drm/card{card_num}/device"
        
        # Find hwmon path if not provided
        if not hwmon_path:
            base_path = f"{self.card_path}/hwmon"
            hwmon_dirs = os.listdir(base_path)
            if hwmon_dirs:
                self.hwmon_path = f"{base_path}/{hwmon_dirs[0]}"
            else:
                raise Exception("No hwmon directory found")
        else:
            self.hwmon_path = hwmon_path

        # Set performance mode first
        self.set_performance_mode(perf_mode)
        
        # Set power limit
        self.set_power_limit(power_limit)

    def get_power_limits(self):
        """Get current, min, and max power limits"""
        try:
            with open(f"{self.hwmon_path}/power1_cap", 'r') as f:
                current = int(f.read().strip()) / 1000000  # Convert to watts
            with open(f"{self.hwmon_path}/power1_cap_min", 'r') as f:
                min_power = int(f.read().strip()) / 1000000
            with open(f"{self.hwmon_path}/power1_cap_max", 'r') as f:
                max_power = int(f.read().strip()) / 1000000
            return current, min_power, max_power
        except Exception as e:
            print(f"Warning: Could not read power limits: {e}")
            return None, None, None

    def set_power_limit(self, watts=None):
        """Set power limit in watts"""
        try:
            current, min_power, max_power = self.get_power_limits()
            if current is None:
                return
            
            # If no power limit specified, set to maximum
            if watts is None:
                watts = max_power
            
            # Ensure watts is within valid range
            watts = max(min_power, min(watts, max_power))
            
            # Convert to microwatts for writing
            microwatts = int(watts * 1000000)
            
            with open(f"{self.hwmon_path}/power1_cap", 'w') as f:
                f.write(str(microwatts))
            
            current, _, _ = self.get_power_limits()
            print(f"Set power limit to: {current:.1f}W (min: {min_power:.1f}W, max: {max_power:.1f}W)")
        except Exception as e:
            print(f"Warning: Could not set power limit: {e}")

    def set_performance_mode(self, mode):
        """Set GPU performance mode"""
        try:
            perf_path = f"{self.card_path}/power_dpm_force_performance_level"
            with open(perf_path, 'w') as f:
                f.write(mode)
            print(f"Set performance mode to: {mode}")
        except Exception as e:
            print(f"Warning: Could not set performance mode: {e}")

    def read_temp(self):
        """Read current GPU temperature"""
        with open(f"{self.hwmon_path}/temp1_input", 'r') as f:
            return int(f.read().strip()) / 1000

    def set_fan_speed(self, speed):
        """Set fan speed (0-255)"""
        with open(f"{self.hwmon_path}/pwm1_enable", 'w') as f:
            f.write("1")
        with open(f"{self.hwmon_path}/pwm1", 'w') as f:
            f.write(str(int(speed)))

    def get_gpu_usage(self):
        """Get GPU usage percentage"""
        try:
            with open(f"{self.card_path}/gpu_busy_percent", 'r') as f:
                return int(f.read().strip())
        except:
            return 0

    def get_vram_usage(self):
        """Get VRAM usage percentage"""
        try:
            with open(f"{self.card_path}/mem_info_vram_used", 'r') as f:
                used = int(f.read().strip())
            with open(f"{self.card_path}/mem_info_vram_total", 'r') as f:
                total = int(f.read().strip())
            return int((used / total) * 100)
        except:
            return 0

    def get_power_usage(self):
        """Get average power usage in watts"""
        try:
            with open(f"{self.hwmon_path}/power1_average", 'r') as f:
                return int(f.read().strip()) / 1000000
        except:
            return 0

    def get_power_cap(self):
        """Get current power cap in watts"""
        current, _, _ = self.get_power_limits()
        return current if current is not None else 0

    def get_performance_mode(self):
        """Get current performance mode"""
        try:
            with open(f"{self.card_path}/power_dpm_force_performance_level", 'r') as f:
                return f.read().strip()
        except:
            return "unknown"

    def adjust_fan(self):
        """Adjust fan speed based on temperature"""
        current_temp = self.read_temp()
        
        # Simple proportional control
        temp_diff = current_temp - self.target_temp
        base_speed = 100
        
        if temp_diff > 0:
            fan_speed = min(255, base_speed + (temp_diff * 10))
        else:
            fan_speed = max(50, base_speed + (temp_diff * 5))
            
        self.set_fan_speed(fan_speed)
        
        # Calculate fan percentage
        fan_pct = round((fan_speed / 255) * 100)
        
        return {
            'temp': current_temp,
            'fan_pct': fan_pct,
            'vram_pct': self.get_vram_usage(),
            'gpu_pct': self.get_gpu_usage(),
            'power': self.get_power_usage(),
            'power_cap': self.get_power_cap(),
            'perf_mode': self.get_performance_mode()
        }

    def run(self):
        """Main control loop"""
        def signal_handler(signum, frame):
            print("\nStopping GPU temperature control...")
            self.running = False
            
        signal.signal(signal.SIGINT, signal_handler)
        
        # Print header
        print("\nGPU Temperature Controller")
        print(f"Card: {self.card_num} | Target: {self.target_temp}°C")
        print("\nGPU  Temp   Fan%   VRAM%  GPU%   Power   Cap    Mode")
        print("-" * 60)
        
        while self.running:
            try:
                stats = self.adjust_fan()
                print(f"{self.card_num:3d}  {stats['temp']:5.1f}°C {stats['fan_pct']:3d}%   "
                      f"{stats['vram_pct']:3d}%   {stats['gpu_pct']:3d}%   "
                      f"{stats['power']:5.1f}W  {stats['power_cap']:5.1f}W  "
                      f"{stats['perf_mode']:<8}", end='\r')
                time.sleep(2)
            except Exception as e:
                print(f"\nError: {e}")
                self.running = False
        
        # Reset fan control to automatic
        with open(f"{self.hwmon_path}/pwm1_enable", 'w') as f:
            f.write("2")

def main():
    parser = argparse.ArgumentParser(description='GPU Temperature Controller')
    parser.add_argument('-c', '--card', type=int, default=0,
                      help='GPU card number (default: 0)')
    parser.add_argument('-t', '--temp', type=float, default=70,
                      help='Target temperature in Celsius (default: 70)')
    parser.add_argument('-p', '--performance', type=str, default='high',
                      choices=['auto', 'low', 'high', 'manual'],
                      help='Performance mode (default: high)')
    parser.add_argument('-w', '--power', type=float,
                      help='Power limit in watts (default: maximum available)')
    
    args = parser.parse_args()
    
    try:
        controller = GPUTempController(
            card_num=args.card,
            target_temp=args.temp,
            perf_mode=args.performance,
            power_limit=args.power
        )
        controller.run()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
