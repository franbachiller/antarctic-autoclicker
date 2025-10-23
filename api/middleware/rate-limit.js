const rateLimit = new Map();

export function checkRateLimit(identifier, maxRequests = 5, windowMs = 60000) {
  const now = Date.now();
  const userRequests = rateLimit.get(identifier) || [];
  
  // Clean old requests
  const recentRequests = userRequests.filter(time => now - time < windowMs);
  
  if (recentRequests.length >= maxRequests) {
    return { 
      allowed: false, 
      retryAfter: Math.ceil((recentRequests[0] + windowMs - now) / 1000)
    };
  }
  
  recentRequests.push(now);
  rateLimit.set(identifier, recentRequests);
  return { allowed: true };
}

// Cleanup old entries every 5 minutes
setInterval(() => {
  const now = Date.now();
  for (const [key, requests] of rateLimit.entries()) {
    const recent = requests.filter(time => now - time < 300000);
    if (recent.length === 0) {
      rateLimit.delete(key);
    } else {
      rateLimit.set(key, recent);
    }
  }
}, 300000);

