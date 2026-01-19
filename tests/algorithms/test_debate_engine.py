"""
Tests for Debate Engine

Covers: blind drafting, sparse topology, convergence detection
"""

import pytest
from mcp_core.algorithms.debate_engine import (
    DebateEngine, DebateState, DebatePhase, Critique, SpeakerConstraints
)


class TestDebateEngine:
    """Test suite for Debate Engine"""
    
    @pytest.fixture
    def engine(self):
        """Create a fresh debate engine"""
        return DebateEngine(max_rounds=5, convergence_threshold=2)
    
    @pytest.fixture
    def agents(self):
        """Standard agent list"""
        return ["agent_1", "agent_2", "agent_3"]


class TestStartDebate(TestDebateEngine):
    """Tests for debate initialization"""
    
    def test_start_debate(self, engine, agents):
        """Should initialize debate state"""
        state = engine.start_debate("debate_1", agents, topology="ring")
        
        assert state.agents == agents
        assert state.phase == DebatePhase.BLIND_DRAFT
        assert state.current_round == 0
        assert state.topology == "ring"
    
    def test_minimum_agents(self, engine):
        """Should require at least 2 agents"""
        with pytest.raises(ValueError):
            engine.start_debate("debate_1", ["agent_1"])
    
    def test_debate_stored(self, engine, agents):
        """Should store debate in active debates"""
        engine.start_debate("debate_1", agents)
        
        assert "debate_1" in engine.active_debates


class TestBlindDraftPhase(TestDebateEngine):
    """Tests for blind drafting"""
    
    def test_collect_drafts(self, engine, agents):
        """Should collect drafts and transition phase"""
        engine.start_debate("debate_1", agents)
        
        drafts = {
            "agent_1": "Draft from agent 1",
            "agent_2": "Draft from agent 2",
            "agent_3": "Draft from agent 3"
        }
        
        engine.blind_draft_phase("debate_1", drafts)
        
        state = engine.active_debates["debate_1"]
        assert state.drafts == drafts
        assert state.phase == DebatePhase.CRITIQUE
    
    def test_wrong_phase_raises(self, engine, agents):
        """Should reject drafts if not in BLIND_DRAFT phase"""
        engine.start_debate("debate_1", agents)
        engine.blind_draft_phase("debate_1", {"agent_1": "draft"})
        
        # Now in CRITIQUE phase
        with pytest.raises(ValueError):
            engine.blind_draft_phase("debate_1", {"agent_1": "another draft"})


class TestTopologyPairings(TestDebateEngine):
    """Tests for sparse topology pairings"""
    
    def test_ring_topology(self, engine, agents):
        """Ring: each agent critiques next"""
        state = DebateState(agents=agents, topology="ring")
        pairings = engine._get_topology_pairings(state)
        
        # In ring, agent_1 -> agent_2, agent_2 -> agent_3, agent_3 -> agent_1
        assert len(pairings) == 3
        assert ("agent_1", "agent_2") in pairings
        assert ("agent_2", "agent_3") in pairings
        assert ("agent_3", "agent_1") in pairings
    
    def test_pairs_topology(self, engine):
        """Pairs: first half critiques second half"""
        agents = ["a1", "a2", "a3", "a4"]
        state = DebateState(agents=agents, topology="pairs")
        pairings = engine._get_topology_pairings(state)
        
        # First half (a1, a2) pairs with second half (a3, a4)
        assert ("a1", "a3") in pairings
        assert ("a2", "a4") in pairings


class TestRevisionPhase(TestDebateEngine):
    """Tests for revision and convergence"""
    
    def test_revision_increments_round(self, engine, agents):
        """Should increment round counter"""
        engine.start_debate("debate_1", agents)
        engine.blind_draft_phase("debate_1", {a: f"draft_{a}" for a in agents})
        
        # Skip critique to test revision
        engine.active_debates["debate_1"].phase = DebatePhase.REVISION
        
        engine.revision_phase("debate_1", {a: f"revised_{a}" for a in agents})
        
        state = engine.active_debates["debate_1"]
        assert state.current_round == 1
    
    def test_convergence_on_no_changes(self, engine, agents):
        """Should converge when drafts don't change"""
        engine.start_debate("debate_1", agents)
        drafts = {a: f"draft_{a}" for a in agents}
        engine.blind_draft_phase("debate_1", drafts)
        
        # Skip to revision
        engine.active_debates["debate_1"].phase = DebatePhase.REVISION
        
        # Submit same drafts (no changes)
        converged = engine.revision_phase("debate_1", drafts)
        
        assert converged
        assert engine.active_debates["debate_1"].phase == DebatePhase.CONVERGED


class TestSpeakerSelection(TestDebateEngine):
    """Tests for dynamic speaker selection"""
    
    def test_no_consecutive_repeats(self, engine, agents):
        """Should not select previous speaker"""
        state = DebateState(agents=agents)
        constraints = SpeakerConstraints(
            no_consecutive_repeats=True,
            previous_speaker="agent_1"
        )
        
        selected = engine.select_next_speaker(state, constraints)
        
        assert selected != "agent_1"
    
    def test_returns_none_if_no_valid(self, engine):
        """Should return None if no valid speakers"""
        state = DebateState(agents=["agent_1"])
        constraints = SpeakerConstraints(
            no_consecutive_repeats=True,
            previous_speaker="agent_1"
        )
        
        selected = engine.select_next_speaker(state, constraints)
        
        assert selected is None


class TestGetFinalConsensus(TestDebateEngine):
    """Tests for final consensus retrieval"""
    
    def test_get_final_drafts(self, engine, agents):
        """Should return final drafts after convergence"""
        engine.start_debate("debate_1", agents)
        engine.blind_draft_phase("debate_1", {a: f"final_{a}" for a in agents})
        engine.active_debates["debate_1"].phase = DebatePhase.CONVERGED
        
        final = engine.get_final_consensus("debate_1")
        
        assert final == {a: f"final_{a}" for a in agents}
