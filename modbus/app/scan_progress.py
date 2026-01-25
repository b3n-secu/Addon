"""
Scan Progress Tracker
Provides real-time progress updates for network scanning operations
"""

import threading
import time
from datetime import datetime
from typing import Optional, Dict, List
import ipaddress


class ScanProgress:
    """
    Tracks the progress of network scanning operations
    Thread-safe implementation for concurrent access
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._active = False
        self._current_ip: Optional[str] = None
        self._total_hosts = 0
        self._scanned_hosts = 0
        self._found_devices: List[Dict] = []
        self._start_time: Optional[datetime] = None
        self._network: Optional[str] = None
        self._scan_type: str = 'unknown'
        self._phase: str = 'idle'  # idle, scanning, finishing, complete
        self._error: Optional[str] = None

    def start_scan(self, network: str, scan_type: str = 'nmap'):
        """Start tracking a new scan"""
        with self._lock:
            self._active = True
            self._network = network
            self._scan_type = scan_type
            self._current_ip = None
            self._scanned_hosts = 0
            self._found_devices = []
            self._start_time = datetime.now()
            self._phase = 'scanning'
            self._error = None

            # Calculate total hosts in network
            try:
                net = ipaddress.IPv4Network(network, strict=False)
                self._total_hosts = net.num_addresses - 2  # Exclude network and broadcast
                if self._total_hosts < 1:
                    self._total_hosts = 1
            except:
                self._total_hosts = 254  # Default for /24

    def update_progress(self, current_ip: str, scanned_count: Optional[int] = None):
        """Update the current scanning progress"""
        with self._lock:
            self._current_ip = current_ip
            if scanned_count is not None:
                self._scanned_hosts = scanned_count
            else:
                self._scanned_hosts += 1

    def add_found_device(self, device: Dict):
        """Add a discovered device to the list"""
        with self._lock:
            self._found_devices.append(device)

    def set_phase(self, phase: str):
        """Set the current scan phase"""
        with self._lock:
            self._phase = phase

    def set_error(self, error: str):
        """Set an error message"""
        with self._lock:
            self._error = error
            self._phase = 'error'

    def finish_scan(self):
        """Mark the scan as complete"""
        with self._lock:
            self._active = False
            self._phase = 'complete'
            self._current_ip = None

    def reset(self):
        """Reset all progress tracking"""
        with self._lock:
            self._active = False
            self._current_ip = None
            self._total_hosts = 0
            self._scanned_hosts = 0
            self._found_devices = []
            self._start_time = None
            self._network = None
            self._scan_type = 'unknown'
            self._phase = 'idle'
            self._error = None

    def get_status(self) -> Dict:
        """Get the current scan status"""
        with self._lock:
            elapsed_seconds = 0
            if self._start_time:
                elapsed_seconds = (datetime.now() - self._start_time).total_seconds()

            # Calculate progress percentage
            progress_percent = 0
            if self._total_hosts > 0:
                progress_percent = min(100, int((self._scanned_hosts / self._total_hosts) * 100))

            # Estimate remaining time
            eta_seconds = 0
            if self._scanned_hosts > 0 and elapsed_seconds > 0:
                rate = self._scanned_hosts / elapsed_seconds
                remaining_hosts = self._total_hosts - self._scanned_hosts
                if rate > 0:
                    eta_seconds = int(remaining_hosts / rate)

            return {
                'active': self._active,
                'phase': self._phase,
                'scan_type': self._scan_type,
                'network': self._network,
                'current_ip': self._current_ip,
                'total_hosts': self._total_hosts,
                'scanned_hosts': self._scanned_hosts,
                'progress_percent': progress_percent,
                'found_devices': len(self._found_devices),
                'devices': self._found_devices.copy(),
                'elapsed_seconds': int(elapsed_seconds),
                'eta_seconds': eta_seconds,
                'error': self._error
            }


# Global scan progress instance
scan_progress = ScanProgress()
