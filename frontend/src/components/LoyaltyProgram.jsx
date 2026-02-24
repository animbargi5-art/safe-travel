import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

export default function LoyaltyProgram({ className = '' }) {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [rewards, setRewards] = useState([]);
  const [offers, setOffers] = useState([]);
  const [upgradeOpportunities, setUpgradeOpportunities] = useState(null);
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      fetchLoyaltyData();
    }
  }, [user]);

  const fetchLoyaltyData = async () => {
    setLoading(true);
    try {
      const [profileRes, rewardsRes, offersRes, upgradeRes] = await Promise.all([
        api.get('/loyalty/profile'),
        api.get('/loyalty/rewards'),
        api.get('/loyalty/offers'),
        api.get('/loyalty/upgrade-opportunities')
      ]);

      setProfile(profileRes.data);
      setRewards(rewardsRes.data.rewards);
      setOffers(offersRes.data.offers);
      setUpgradeOpportunities(upgradeRes.data);
    } catch (error) {
      console.error('Failed to fetch loyalty data:', error);
    } finally {
      setLoading(false);
    }
  };

  const redeemReward = async (rewardId) => {
    try {
      const response = await api.post('/loyalty/redeem', { reward_id: rewardId });
      
      if (response.data.success) {
        alert(`Successfully redeemed ${response.data.redemption.reward_name}!`);
        fetchLoyaltyData(); // Refresh data
      }
    } catch (error) {
      console.error('Failed to redeem reward:', error);
      alert('Failed to redeem reward. Please try again.');
    }
  };

  const getTierColor = (tier) => {
    const colors = {
      'BRONZE': 'from-amber-600 to-amber-800',
      'SILVER': 'from-gray-400 to-gray-600',
      'GOLD': 'from-yellow-400 to-yellow-600',
      'PLATINUM': 'from-gray-300 to-gray-500',
      'DIAMOND': 'from-blue-400 to-blue-600'
    };
    return colors[tier] || 'from-gray-400 to-gray-600';
  };

  const getTierIcon = (tier) => {
    const icons = {
      'BRONZE': '🥉',
      'SILVER': '🥈',
      'GOLD': '🥇',
      'PLATINUM': '💎',
      'DIAMOND': '💠'
    };
    return icons[tier] || '🏆';
  };

  if (!user) {
    return (
      <div className={`text-center p-6 bg-gray-50 rounded-lg ${className}`}>
        <p className="text-gray-600">Please log in to view your loyalty program</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className={`animate-pulse ${className}`}>
        <div className="bg-gray-200 rounded-xl h-64 mb-4"></div>
        <div className="space-y-3">
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-xl shadow-lg border border-gray-200 ${className}`}>
      {/* Header with Tier Status */}
      <div className={`bg-gradient-to-r ${getTierColor(profile?.current_tier)} p-6 rounded-t-xl text-white`}>
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-2xl font-bold mb-2">
              {getTierIcon(profile?.current_tier)} {profile?.current_tier} Member
            </h3>
            <p className="text-white/90">
              {profile?.total_points?.toLocaleString()} loyalty points
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-white/80">Member Since</div>
            <div className="font-semibold">
              {profile?.lifetime_stats?.member_since || '2024'}
            </div>
          </div>
        </div>

        {/* Tier Progress */}
        {profile?.tier_progress?.next_tier && (
          <div className="mt-4">
            <div className="flex justify-between text-sm text-white/90 mb-1">
              <span>Progress to {profile.tier_progress.next_tier}</span>
              <span>{profile.tier_progress.points_to_next} points to go</span>
            </div>
            <div className="w-full bg-white/20 rounded-full h-2">
              <div 
                className="bg-white rounded-full h-2 transition-all duration-500"
                style={{ width: `${profile.tier_progress.progress_percentage}%` }}
              ></div>
            </div>
          </div>
        )}
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex">
          {[
            { id: 'profile', label: 'Profile', icon: '👤' },
            { id: 'rewards', label: 'Rewards', icon: '🎁' },
            { id: 'offers', label: 'Offers', icon: '🎯' },
            { id: 'upgrade', label: 'Upgrade', icon: '⬆️' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center px-6 py-3 font-medium text-sm ${
                activeTab === tab.id
                  ? 'text-purple-600 border-b-2 border-purple-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      <div className="p-6">
        <AnimatePresence mode="wait">
          {activeTab === 'profile' && (
            <motion.div
              key="profile"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              {/* Tier Benefits */}
              <div className="mb-6">
                <h4 className="font-semibold text-gray-800 mb-3">🎯 Your Tier Benefits</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-3 bg-blue-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">
                      {profile.tier_benefits.points_multiplier}x
                    </div>
                    <div className="text-sm text-gray-600">Points Multiplier</div>
                  </div>
                  <div className="text-center p-3 bg-green-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">
                      {profile.tier_benefits.discount_percentage}%
                    </div>
                    <div className="text-sm text-gray-600">Discount</div>
                  </div>
                  <div className="text-center p-3 bg-purple-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">
                      {profile.tier_benefits.extra_baggage}
                    </div>
                    <div className="text-sm text-gray-600">Extra Bags</div>
                  </div>
                  <div className="text-center p-3 bg-orange-50 rounded-lg">
                    <div className="text-2xl font-bold text-orange-600">
                      {(profile.tier_benefits.upgrade_probability * 100).toFixed(0)}%
                    </div>
                    <div className="text-sm text-gray-600">Upgrade Chance</div>
                  </div>
                </div>
              </div>

              {/* Lifetime Stats */}
              <div className="mb-6">
                <h4 className="font-semibold text-gray-800 mb-3">📊 Lifetime Statistics</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-lg font-bold text-gray-800">
                      {profile.lifetime_stats.total_bookings}
                    </div>
                    <div className="text-sm text-gray-600">Total Bookings</div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-lg font-bold text-gray-800">
                      ${profile.lifetime_stats.total_spent?.toLocaleString()}
                    </div>
                    <div className="text-sm text-gray-600">Total Spent</div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="text-lg font-bold text-gray-800">
                      {profile.lifetime_stats.destinations_visited}
                    </div>
                    <div className="text-sm text-gray-600">Destinations</div>
                  </div>
                </div>
              </div>

              {/* Recent Activity */}
              <div>
                <h4 className="font-semibold text-gray-800 mb-3">🕒 Recent Activity</h4>
                <div className="space-y-3">
                  {profile.recent_activity?.slice(0, 5).map((activity, index) => (
                    <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                      <div>
                        <div className="font-medium text-gray-800">{activity.description}</div>
                        <div className="text-sm text-gray-600">
                          {new Date(activity.date).toLocaleDateString()}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-green-600">+{activity.points_earned}</div>
                        <div className="text-sm text-gray-600">points</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'rewards' && (
            <motion.div
              key="rewards"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <div className="mb-4 flex justify-between items-center">
                <h4 className="font-semibold text-gray-800">🎁 Available Rewards</h4>
                <div className="text-sm text-gray-600">
                  You have {profile?.available_points?.toLocaleString()} points
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {rewards.map((reward) => (
                  <motion.div
                    key={reward.id}
                    whileHover={{ scale: 1.02 }}
                    className={`border rounded-lg p-4 ${
                      reward.can_afford 
                        ? 'border-green-200 bg-green-50' 
                        : 'border-gray-200 bg-gray-50'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h5 className="font-semibold text-gray-800">{reward.name}</h5>
                        <p className="text-sm text-gray-600 mt-1">{reward.description}</p>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-purple-600">
                          {reward.points_cost.toLocaleString()}
                        </div>
                        <div className="text-xs text-gray-500">points</div>
                      </div>
                    </div>

                    <div className="flex justify-between items-center">
                      <div className="text-sm text-gray-600">
                        Value: ${reward.value} • Valid: {reward.validity_days} days
                      </div>
                      <button
                        onClick={() => redeemReward(reward.id)}
                        disabled={!reward.can_afford}
                        className={`px-4 py-2 rounded text-sm font-medium ${
                          reward.can_afford
                            ? 'bg-purple-600 text-white hover:bg-purple-700'
                            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                        }`}
                      >
                        {reward.can_afford ? 'Redeem' : `Need ${reward.points_needed} more`}
                      </button>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {activeTab === 'offers' && (
            <motion.div
              key="offers"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <h4 className="font-semibold text-gray-800 mb-4">🎯 Personalized Offers</h4>
              
              <div className="space-y-4">
                {offers.map((offer, index) => (
                  <motion.div
                    key={offer.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="border border-orange-200 bg-orange-50 rounded-lg p-4"
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h5 className="font-semibold text-orange-800">{offer.title}</h5>
                        <p className="text-orange-700 mt-1">{offer.description}</p>
                        <p className="text-sm text-orange-600 mt-2">{offer.conditions}</p>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-orange-800">
                          {offer.type === 'POINTS_MULTIPLIER' && `${offer.value}x Points`}
                          {offer.type === 'SEASONAL_DISCOUNT' && `${offer.value}% Off`}
                          {offer.type === 'REFERRAL' && `${offer.value} Points`}
                        </div>
                        <div className="text-xs text-orange-600">
                          Expires: {new Date(offer.expires_at).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {activeTab === 'upgrade' && upgradeOpportunities && (
            <motion.div
              key="upgrade"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <h4 className="font-semibold text-gray-800 mb-4">⬆️ Tier Upgrade Opportunities</h4>
              
              <div className="mb-6 p-4 bg-blue-50 rounded-lg">
                <div className="text-center">
                  <div className="text-lg font-semibold text-blue-800">
                    Current: {upgradeOpportunities.current_tier}
                  </div>
                  <div className="text-blue-600">
                    {upgradeOpportunities.current_points.toLocaleString()} points
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                {upgradeOpportunities.upgrade_opportunities?.map((opportunity, index) => (
                  <motion.div
                    key={opportunity.tier}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="border border-gray-200 rounded-lg p-4"
                  >
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h5 className="font-semibold text-gray-800 flex items-center">
                          {getTierIcon(opportunity.tier)} {opportunity.tier} Tier
                        </h5>
                        <p className="text-sm text-gray-600 mt-1">
                          {opportunity.points_needed.toLocaleString()} points needed
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-green-600">
                          ${opportunity.estimated_annual_savings.toFixed(0)}
                        </div>
                        <div className="text-xs text-gray-500">annual savings</div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                      <div>
                        <span className="text-gray-500">Discount:</span>
                        <div className="font-medium">{opportunity.benefits.discount_percentage}%</div>
                      </div>
                      <div>
                        <span className="text-gray-500">Points:</span>
                        <div className="font-medium">{opportunity.benefits.points_multiplier}x</div>
                      </div>
                      <div>
                        <span className="text-gray-500">Lounge:</span>
                        <div className="font-medium">
                          {opportunity.benefits.lounge_access ? '✅' : '❌'}
                        </div>
                      </div>
                      <div>
                        <span className="text-gray-500">Baggage:</span>
                        <div className="font-medium">+{opportunity.benefits.extra_baggage}</div>
                      </div>
                    </div>

                    <div className="mt-3 text-sm text-gray-600">
                      Approximately {opportunity.bookings_needed} more bookings needed
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}