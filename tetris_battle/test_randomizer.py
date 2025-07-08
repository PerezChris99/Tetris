#!/usr/bin/env python3
"""Test script to verify that all 7 tetrominoes appear in the randomizer"""

from tetromino import GameBoyRandomizer

def test_randomizer():
    """Test that all 7 pieces appear in the randomizer"""
    print("Testing Game Boy Tetris randomizer...")
    
    randomizer = GameBoyRandomizer()
    pieces_seen = set()
    
    # Generate 50 pieces to ensure we see all 7
    for i in range(50):
        piece = randomizer.get_next()
        pieces_seen.add(piece.shape_type)
        print(f"Piece {i+1}: {piece.shape_type}")
        
        # If we've seen all 7 pieces, we can stop early
        if len(pieces_seen) == 7:
            print(f"\nAll 7 pieces found after {i+1} pieces!")
            break
    
    print(f"\nPieces seen: {sorted(pieces_seen)}")
    print(f"Total unique pieces: {len(pieces_seen)}")
    
    expected_shapes = {'I', 'J', 'L', 'O', 'S', 'T', 'Z'}
    if pieces_seen == expected_shapes:
        print("✓ SUCCESS: All 7 tetrominoes are appearing correctly!")
    else:
        missing = expected_shapes - pieces_seen
        print(f"✗ FAILED: Missing pieces: {missing}")

if __name__ == "__main__":
    test_randomizer()
