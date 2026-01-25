"""
Auto Scanner - Automatic network scanning with configurable intervals
Handles automatic device discovery, register scanning, and config generation
"""

import threading
import time
import logging
from datetime import datetime
from typing import Optional, Dict, List, Callable

logger = logging.getLogger(__name__)


class AutoScanner:
    """
    Manages automatic network scanning at configurable intervals
    """

    def __init__(self):
        self.scan_interval = 300  # Default: 5 minutes
        self.enabled = False
        self.last_scan_time: Optional[datetime] = None
        self.last_scan_results: Dict = {}
        self.scan_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.scan_in_progress = False
        self.scan_callbacks: List[Callable] = []

        # Scan settings
        self.use_nmap = True  # Prefer nmap if available
        self.auto_add_devices = True
        self.auto_register_scan = True
        self.auto_generate_config = False
        self.network: Optional[str] = None  # Auto-detect if None
        self.port_range = '102,502,510,20000-20100'

    def set_interval(self, seconds: int):
        """Set scan interval in seconds (minimum 60 seconds)"""
        self.scan_interval = max(60, seconds)
        logger.info(f"Auto-scan interval set to {self.scan_interval} seconds")

    def set_network(self, network: Optional[str]):
        """Set network to scan (None for auto-detect)"""
        self.network = network
        logger.info(f"Auto-scan network set to {network or 'auto-detect'}")

    def set_port_range(self, port_range: str):
        """Set port range for scanning"""
        self.port_range = port_range
        logger.info(f"Auto-scan port range set to {port_range}")

    def configure(self, config: Dict):
        """Configure auto-scanner from dictionary"""
        if 'interval' in config:
            self.set_interval(config['interval'])
        if 'network' in config:
            self.set_network(config['network'])
        if 'port_range' in config:
            self.set_port_range(config['port_range'])
        if 'use_nmap' in config:
            self.use_nmap = config['use_nmap']
        if 'auto_add_devices' in config:
            self.auto_add_devices = config['auto_add_devices']
        if 'auto_register_scan' in config:
            self.auto_register_scan = config['auto_register_scan']
        if 'auto_generate_config' in config:
            self.auto_generate_config = config['auto_generate_config']

    def add_callback(self, callback: Callable):
        """Add callback function to be called after each scan"""
        self.scan_callbacks.append(callback)

    def remove_callback(self, callback: Callable):
        """Remove a callback function"""
        if callback in self.scan_callbacks:
            self.scan_callbacks.remove(callback)

    def start(self, scan_func: Callable, nmap_available: bool = False):
        """Start automatic scanning"""
        if self.enabled:
            logger.warning("Auto-scanner already running")
            return False

        self.enabled = True
        self.stop_event.clear()
        self.scan_thread = threading.Thread(
            target=self._scan_loop,
            args=(scan_func, nmap_available),
            daemon=True
        )
        self.scan_thread.start()
        logger.info(f"Auto-scanner started with {self.scan_interval}s interval")
        return True

    def stop(self):
        """Stop automatic scanning"""
        if not self.enabled:
            return False

        self.enabled = False
        self.stop_event.set()
        if self.scan_thread:
            self.scan_thread.join(timeout=5)
        logger.info("Auto-scanner stopped")
        return True

    def _scan_loop(self, scan_func: Callable, nmap_available: bool):
        """Main scanning loop"""
        while self.enabled and not self.stop_event.is_set():
            try:
                self._perform_scan(scan_func, nmap_available)
            except Exception as e:
                logger.error(f"Error in auto-scan: {e}", exc_info=True)

            # Wait for next interval or stop signal
            self.stop_event.wait(timeout=self.scan_interval)

    def _perform_scan(self, scan_func: Callable, nmap_available: bool):
        """Perform a single scan cycle"""
        if self.scan_in_progress:
            logger.warning("Scan already in progress, skipping")
            return

        self.scan_in_progress = True
        self.last_scan_time = datetime.now()

        try:
            logger.info("Auto-scan starting...")

            # Determine scan method
            use_nmap = self.use_nmap and nmap_available

            # Call the provided scan function
            results = scan_func(
                network=self.network,
                port_range=self.port_range,
                use_nmap=use_nmap,
                auto_add=self.auto_add_devices
            )

            self.last_scan_results = {
                'timestamp': self.last_scan_time.isoformat(),
                'method': 'nmap' if use_nmap else 'python',
                'network': self.network or 'auto-detected',
                'devices_found': len(results.get('devices', [])),
                'devices': results.get('devices', []),
                'success': results.get('success', False)
            }

            logger.info(f"Auto-scan complete: {self.last_scan_results['devices_found']} devices found")

            # Execute callbacks
            for callback in self.scan_callbacks:
                try:
                    callback(self.last_scan_results)
                except Exception as e:
                    logger.error(f"Error in scan callback: {e}")

        finally:
            self.scan_in_progress = False

    def get_status(self) -> Dict:
        """Get current auto-scanner status"""
        return {
            'enabled': self.enabled,
            'interval': self.scan_interval,
            'network': self.network,
            'port_range': self.port_range,
            'use_nmap': self.use_nmap,
            'auto_add_devices': self.auto_add_devices,
            'auto_register_scan': self.auto_register_scan,
            'auto_generate_config': self.auto_generate_config,
            'scan_in_progress': self.scan_in_progress,
            'last_scan_time': self.last_scan_time.isoformat() if self.last_scan_time else None,
            'last_scan_results': self.last_scan_results
        }

    def trigger_manual_scan(self, scan_func: Callable, nmap_available: bool = False) -> Dict:
        """Trigger a manual scan outside the automatic interval"""
        if self.scan_in_progress:
            return {
                'success': False,
                'error': 'Scan already in progress'
            }

        self._perform_scan(scan_func, nmap_available)
        return {
            'success': True,
            'results': self.last_scan_results
        }


# Global auto-scanner instance
auto_scanner = AutoScanner()
