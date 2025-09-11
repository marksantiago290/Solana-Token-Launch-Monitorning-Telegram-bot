"""
Scheduler service for running periodic tasks like checking for new PumpFun tokens.
"""

import logging
import asyncio
from datetime import datetime
from typing import Optional

from services.notification_service import notification_service

logger = logging.getLogger(__name__)

class SchedulerService:
    """Service for managing scheduled tasks"""
    
    def __init__(self):
        self.is_running = False
        self.check_interval = 30  # Check every 60 seconds (1 minute)
        self.task: Optional[asyncio.Task] = None
        
    async def start_monitoring(self) -> None:
        """Start the PumpFun token monitoring task"""
        if self.is_running:
            logger.warning("Monitoring is already running")
            return
        
        self.is_running = True
        self.task = asyncio.create_task(self._monitoring_loop())
        logger.info("Started PumpFun token monitoring")
    
    async def stop_monitoring(self) -> None:
        """Stop the PumpFun token monitoring task"""
        if not self.is_running:
            logger.warning("Monitoring is not running")
            return
        
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped PumpFun token monitoring")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop that runs every minute"""
        logger.info("Starting PumpFun token monitoring loop")
        
        while self.is_running:
            try:
                start_time = datetime.now()
                
                # Check for new tokens
                new_tokens = await notification_service.check_for_new_tokens()
                
                # Send notifications if new tokens found
                if new_tokens:
                    await notification_service.send_notifications(new_tokens)
                
                # Calculate sleep time to maintain 1-minute intervals
                elapsed = (datetime.now() - start_time).total_seconds()
                sleep_time = max(0, self.check_interval - elapsed)
                
                logger.info(f"Monitoring cycle completed in {elapsed:.2f}s. Sleeping for {sleep_time:.2f}s")
                
                # Sleep until next check
                await asyncio.sleep(sleep_time)
                
            except asyncio.CancelledError:
                logger.info("Monitoring loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                # Sleep for a shorter time on error to retry sooner
                await asyncio.sleep(30)
    
    async def run_single_check(self) -> dict:
        """
        Run a single check for new tokens (useful for testing or manual triggers)
        
        Returns:
            dict: Results of the check
        """
        try:
            logger.info("Running single PumpFun token check")
            
            start_time = datetime.now()
            new_tokens = await notification_service.check_for_new_tokens()
            
            if new_tokens:
                await notification_service.send_notifications(new_tokens)
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            result = {
                "success": True,
                "new_tokens_found": len(new_tokens),
                "execution_time": elapsed,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Single check completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in single check: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_status(self) -> dict:
        """Get the current status of the scheduler"""
        return {
            "is_running": self.is_running,
            "check_interval": self.check_interval,
            "task_running": self.task is not None and not self.task.done() if self.task else False
        }

# Global scheduler service instance
scheduler_service = SchedulerService()
