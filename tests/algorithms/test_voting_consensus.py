"""
Tests for Weighted Voting Consensus

Covers: vote registration, weighted aggregation, Elo ratings
"""

import pytest
from mcp_core.algorithms.voting_consensus import (
    WeightedVotingConsensus, Vote, ConsensusResult
)


class TestWeightedVotingConsensus:
    """Test suite for Weighted Voting Consensus"""
    
    @pytest.fixture
    def consensus(self):
        """Create a fresh consensus engine"""
        return WeightedVotingConsensus(k_factor=32.0, initial_rating=1500.0)


class TestVoteRegistration(TestWeightedVotingConsensus):
    """Tests for vote registration"""
    
    def test_register_single_vote(self, consensus):
        """Should register a vote successfully"""
        consensus.register_vote("agent_1", "option_A", 0.9, "general")
        
        assert len(consensus.vote_history) == 1
        assert consensus.vote_history[0].agent_id == "agent_1"
        assert consensus.vote_history[0].decision == "option_A"
    
    def test_register_multiple_votes(self, consensus):
        """Should register multiple votes"""
        consensus.register_vote("agent_1", "option_A", 0.9)
        consensus.register_vote("agent_2", "option_B", 0.8)
        consensus.register_vote("agent_3", "option_A", 0.7)
        
        assert len(consensus.vote_history) == 3
    
    def test_invalid_confidence_raises(self, consensus):
        """Should reject confidence outside [0, 1]"""
        with pytest.raises(ValueError):
            consensus.register_vote("agent_1", "option_A", 1.5)
        
        with pytest.raises(ValueError):
            consensus.register_vote("agent_1", "option_A", -0.1)


class TestComputeDecision(TestWeightedVotingConsensus):
    """Tests for decision computation"""
    
    def test_simple_majority(self, consensus):
        """Should select option with most weight"""
        consensus.register_vote("agent_1", "option_A", 0.9)
        consensus.register_vote("agent_2", "option_A", 0.8)
        consensus.register_vote("agent_3", "option_B", 0.6)
        
        result = consensus.compute_decision(use_elo=False)
        
        assert result.decision == "option_A"
        assert result.total_weight == pytest.approx(1.7)
    
    def test_confidence_weighted(self, consensus):
        """Lower confidence should have less weight"""
        consensus.register_vote("agent_1", "option_A", 0.3)
        consensus.register_vote("agent_2", "option_B", 0.9)
        
        result = consensus.compute_decision(use_elo=False)
        
        assert result.decision == "option_B"
    
    def test_vote_distribution(self, consensus):
        """Should track vote distribution"""
        consensus.register_vote("agent_1", "option_A", 0.5)
        consensus.register_vote("agent_2", "option_B", 0.5)
        
        result = consensus.compute_decision(use_elo=False)
        
        assert "option_A" in result.vote_distribution
        assert "option_B" in result.vote_distribution
    
    def test_no_votes_raises(self, consensus):
        """Should raise when no votes registered"""
        with pytest.raises(ValueError):
            consensus.compute_decision()


class TestEloRatings(TestWeightedVotingConsensus):
    """Tests for Elo rating system"""
    
    def test_initial_rating(self, consensus):
        """New agents should have initial rating"""
        rating = consensus.get_agent_rating("new_agent", "general")
        assert rating == 1500.0
    
    def test_rating_increases_on_correct(self, consensus):
        """Rating should increase when agent is correct"""
        old_rating = consensus.get_agent_rating("agent_1", "python")
        new_rating = consensus.update_elo_rating("agent_1", was_correct=True, domain="python")
        
        assert new_rating > old_rating
    
    def test_rating_decreases_on_incorrect(self, consensus):
        """Rating should decrease when agent is incorrect"""
        old_rating = consensus.get_agent_rating("agent_1", "python")
        new_rating = consensus.update_elo_rating("agent_1", was_correct=False, domain="python")
        
        assert new_rating < old_rating
    
    def test_domain_specific_ratings(self, consensus):
        """Different domains should have independent ratings"""
        consensus.update_elo_rating("agent_1", was_correct=True, domain="python")
        consensus.update_elo_rating("agent_1", was_correct=False, domain="sql")
        
        python_rating = consensus.get_agent_rating("agent_1", "python")
        sql_rating = consensus.get_agent_rating("agent_1", "sql")
        
        assert python_rating > sql_rating


class TestClearVotes(TestWeightedVotingConsensus):
    """Tests for vote clearing"""
    
    def test_clear_votes(self, consensus):
        """Should clear vote history but preserve ratings"""
        consensus.register_vote("agent_1", "option_A", 0.9)
        consensus.update_elo_rating("agent_1", was_correct=True)
        
        consensus.clear_votes()
        
        assert len(consensus.vote_history) == 0
        assert consensus.get_agent_rating("agent_1", "general") > 1500.0
