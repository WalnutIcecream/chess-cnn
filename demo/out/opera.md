{
  "game": {
    "game_id": "Paris FRA",
    "source": "game",
    "fen_start": null,
    "split": "",
    "players": {
      "white": "Paul Morphy",
      "black": "Duke of Brunswick and Count Isouard"
    },
    "result": "1-0",
    "moves": [
      {
        "ply": 0,
        "fen_before": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "move_uci": "e2e4",
        "move_san": "e4",
        "quality": {
          "label": "best",
          "eval_before_cp": 30.0,
          "eval_after_cp": 30.0,
          "win_prob_before": 0.5275875538925041,
          "win_prob_after": 0.5275875538925041,
          "loss_cp": 0.0,
          "loss_wp": 0.0,
          "best_move": "e2e4",
          "best_move_san": "e4",
          "best_move_cp": 30.0,
          "best_move_wp": 0.5275875538925041,
          "rank": 1,
          "n_lines": 3,
          "played_in_multipv": true,
          "is_only_move": false,
          "gap_to_second_wp": 0.011943821471083194,
          "sharpness": 0.01378326286318865,
          "is_forcing": false,
          "is_critical": false
        },
        "themes": [
          {
            "theme": "exposes_king",
            "squares": [
              "e1"
            ],
            "pieces": [
              "K@e1"
            ],
            "confidence": 1.0,
            "evidence": "king safety drops from 3.00 to 2.00"
          },
          {
            "theme": "bishop_pair",
            "squares": [
              "c1",
              "f1"
            ],
            "pieces": [
              "B@c1",
              "B@f1"
            ],
            "confidence": 1.0,
            "evidence": "the mover owns both bishops"
          },
          {
            "theme": "bad_bishop",
            "squares": [
              "c1"
            ],
            "pieces": [
              "B@c1"
            ],
            "confidence": 0.7,
            "evidence": "bishop on c1 is blocked by its own pawns"
          },
          {
            "theme": "controls_center",
            "squares": [],
            "pieces": [],
            "confidence": 0.8,
            "evidence": "central control rises from 0.00 to 1.00"
          }
        ],
        "positional_delta": {
          "material": 0.0,
          "mobility": 60.0,
          "king_safety": -12.0,
          "pawn_structure": 0.0,
          "space": 4.0,
          "activity": 0.0
        },
        "intent": [],
        "pv": [
          "e2e4",
          "e7e5",
          "g1f3",
          "b8c6",
          "d2d4",
          "e5d4",
          "f3d4",
          "f8c5",
          "d4c6",
          "b7c6"
        ],
        "fen_after": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 53793,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 1,
        "fen_before": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
        "move_uci": "e7e5",
        "move_san": "e5",
        "quality": {
          "label": "excellent",
          "eval_before_cp": -32.0,
          "eval_after_cp": -41.0,
          "win_prob_before": 0.4705773918729125,
          "win_prob_after": 0.4623301956955016,
          "loss_cp": 9.0,
          "loss_wp": 0.008247196177410876,
          "best_move": "c7c5",
          "best_move_san": "c5",
          "best_move_cp": -32.0,
          "best_move_wp": 0.4705773918729125,
          "rank": 2,
          "n_lines": 3,
          "played_in_multipv": true,
          "is_only_move": false,
          "gap_to_second_wp": 0.008247196177410876,
          "sharpness": 0.01282037081898102,
          "is_forcing": false,
          "is_critical": false
        },
        "themes": [
          {
            "theme": "exposes_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 1.0,
            "evidence": "king safety drops from 3.00 to 2.00"
          },
          {
            "theme": "bishop_pair",
            "squares": [
              "c8",
              "f8"
            ],
            "pieces": [
              "b@c8",
              "b@f8"
            ],
            "confidence": 1.0,
            "evidence": "the mover owns both bishops"
          },
          {
            "theme": "bad_bishop",
            "squares": [
              "c8"
            ],
            "pieces": [
              "b@c8"
            ],
            "confidence": 0.7,
            "evidence": "bishop on c8 is blocked by its own pawns"
          },
          {
            "theme": "controls_center",
            "squares": [],
            "pieces": [],
            "confidence": 0.8,
            "evidence": "central control rises from 0.00 to 1.00"
          }
        ],
        "positional_delta": {
          "material": 0.0,
          "mobility": 60.0,
          "king_safety": -12.0,
          "pawn_structure": 0.0,
          "space": 4.0,
          "activity": 0.0
        },
        "intent": [],
        "pv": [
          "e7e5",
          "g1f3",
          "d7d6",
          "f1c4",
          "f8e7",
          "d2d4",
          "e5d4",
          "f3d4",
          "g8f6",
          "b1c3",
          "e8g8"
        ],
        "fen_after": "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 101921,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 2,
        "fen_before": "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2",
        "move_uci": "g1f3",
        "move_san": "Nf3",
        "quality": {
          "label": "best",
          "eval_before_cp": 27.0,
          "eval_after_cp": 27.0,
          "win_prob_before": 0.5248335896523929,
          "win_prob_after": 0.5248335896523929,
          "loss_cp": 0.0,
          "loss_wp": 0.0,
          "best_move": "g1f3",
          "best_move_san": "Nf3",
          "best_move_cp": 27.0,
          "best_move_wp": 0.5248335896523929,
          "rank": 1,
          "n_lines": 3,
          "played_in_multipv": true,
          "is_only_move": false,
          "gap_to_second_wp": 0.009189857230971987,
          "sharpness": 0.02207205773237897,
          "is_forcing": false,
          "is_critical": false
        },
        "themes": [
          {
            "theme": "bishop_pair",
            "squares": [
              "c1",
              "f1"
            ],
            "pieces": [
              "B@c1",
              "B@f1"
            ],
            "confidence": 1.0,
            "evidence": "the mover owns both bishops"
          },
          {
            "theme": "bad_bishop",
            "squares": [
              "c1"
            ],
            "pieces": [
              "B@c1"
            ],
            "confidence": 0.7,
            "evidence": "bishop on c1 is blocked by its own pawns"
          },
          {
            "theme": "develops_piece",
            "squares": [
              "g1",
              "f3"
            ],
            "pieces": [
              "N@f3"
            ],
            "confidence": 1.0,
            "evidence": "N@f3 develops off the back rank"
          },
          {
            "theme": "controls_center",
            "squares": [],
            "pieces": [],
            "confidence": 0.8,
            "evidence": "central control rises from 1.00 to 3.00"
          }
        ],
        "positional_delta": {
          "material": 0.0,
          "mobility": 0.0,
          "king_safety": 0.0,
          "pawn_structure": 0.0,
          "space": 8.0,
          "activity": 10.0
        },
        "intent": [
          {
            "tag": "improves_piece",
            "evidence": "the N moves toward the centre",
            "moves": [],
            "confidence": 0.7
          },
          {
            "tag": "develops",
            "evidence": "develops the N to f3",
            "moves": [],
            "confidence": 1.0
          }
        ],
        "pv": [
          "g1f3",
          "b8c6",
          "f1b5",
          "a7a6",
          "b5a4",
          "d7d6",
          "d2d4",
          "b7b5",
          "a4b3",
          "e5d4",
          "f3d4",
          "c6d4",
          "d1d4"
        ],
        "fen_after": "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 109414,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 3,
        "fen_before": "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2",
        "move_uci": "d7d6",
        "move_san": "d6",
        "quality": {
          "label": "good",
          "eval_before_cp": -27.0,
          "eval_after_cp": -68.0,
          "win_prob_before": 0.47516641034760715,
          "win_prob_after": 0.4377296159574105,
          "loss_cp": 41.0,
          "loss_wp": 0.03743679439019665,
          "best_move": "g8f6",
          "best_move_san": "Nf6",
          "best_move_cp": -27.0,
          "best_move_wp": 0.47516641034760715,
          "rank": 3,
          "n_lines": 3,
          "played_in_multipv": true,
          "is_only_move": false,
          "gap_to_second_wp": 0.008256692646737562,
          "sharpness": 0.03743679439019665,
          "is_forcing": false,
          "is_critical": false
        },
        "themes": [
          {
            "theme": "bishop_pair",
            "squares": [
              "c8",
              "f8"
            ],
            "pieces": [
              "b@c8",
              "b@f8"
            ],
            "confidence": 1.0,
            "evidence": "the mover owns both bishops"
          },
          {
            "theme": "controls_center",
            "squares": [],
            "pieces": [],
            "confidence": 0.8,
            "evidence": "central control rises from 1.00 to 2.00"
          }
        ],
        "positional_delta": {
          "material": 0.0,
          "mobility": 18.0,
          "king_safety": 0.0,
          "pawn_structure": 0.0,
          "space": 4.0,
          "activity": 0.0
        },
        "intent": [],
        "pv": [
          "d7d6",
          "d2d4",
          "e5d4",
          "f3d4",
          "g8f6",
          "b1c3",
          "f8e7",
          "c1f4",
          "e8g8",
          "d1d2",
          "a7a6",
          "e1c1",
          "b7b5",
          "f1e2",
          "c7c6",
          "h2h3"
        ],
        "fen_after": "rnbqkbnr/ppp2ppp/3p4/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 104170,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 4,
        "fen_before": "rnbqkbnr/ppp2ppp/3p4/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3",
        "move_uci": "d2d4",
        "move_san": "d4",
        "quality": {
          "label": "best",
          "eval_before_cp": 68.0,
          "eval_after_cp": 68.0,
          "win_prob_before": 0.5622703840425896,
          "win_prob_after": 0.5622703840425896,
          "loss_cp": 0.0,
          "loss_wp": 0.0,
          "best_move": "d2d4",
          "best_move_san": "d4",
          "best_move_cp": 68.0,
          "best_move_wp": 0.5622703840425896,
          "rank": 1,
          "n_lines": 3,
          "played_in_multipv": true,
          "is_only_move": false,
          "gap_to_second_wp": 0.026431669571838734,
          "sharpness": 0.03376520673077643,
          "is_forcing": false,
          "is_critical": false
        },
        "themes": [
          {
            "theme": "exposes_king",
            "squares": [
              "e1"
            ],
            "pieces": [
              "K@e1"
            ],
            "confidence": 1.0,
            "evidence": "king safety drops from 2.00 to 1.00"
          },
          {
            "theme": "pawn_break",
            "squares": [
              "d4"
            ],
            "pieces": [
              "P@d4"
            ],
            "confidence": 1.0,
            "evidence": "pawn on d4 attacks an enemy pawn"
          },
          {
            "theme": "bishop_pair",
            "squares": [
              "c1",
              "f1"
            ],
            "pieces": [
              "B@c1",
              "B@f1"
            ],
            "confidence": 1.0,
            "evidence": "the mover owns both bishops"
          }
        ],
        "positional_delta": {
          "material": 0.0,
          "mobility": 48.0,
          "king_safety": -12.0,
          "pawn_structure": 0.0,
          "space": 0.0,
          "activity": 0.0
        },
        "intent": [],
        "pv": [
          "d2d4",
          "e5d4",
          "f3d4",
          "g8f6",
          "b1c3",
          "f8e7",
          "c1f4",
          "a7a6",
          "d1d2",
          "e8g8",
          "e1c1",
          "b7b5",
          "f1e2",
          "c7c6",
          "h2h3"
        ],
        "fen_after": "rnbqkbnr/ppp2ppp/3p4/4p3/3PP3/5N2/PPP2PPP/RNBQKB1R b KQkq - 0 3",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 66096,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 5,
        "fen_before": "rnbqkbnr/ppp2ppp/3p4/4p3/3PP3/5N2/PPP2PPP/RNBQKB1R b KQkq - 0 3",
        "move_uci": "c8g4",
        "move_san": "Bg4",
        "quality": {
          "label": "good",
          "eval_before_cp": -55.0,
          "eval_after_cp": -78.0,
          "win_prob_before": 0.44954372531791664,
          "win_prob_after": 0.4286889425850106,
          "loss_cp": 23.0,
          "loss_wp": 0.02085478273290603,
          "best_move": "b8d7",
          "best_move_san": "Nd7",
          "best_move_cp": -55.0,
          "best_move_wp": 0.44954372531791664,
          "rank": null,
          "n_lines": 3,
          "played_in_multipv": false,
          "is_only_move": false,
          "gap_to_second_wp": 0.006369386284420242,
          "sharpness": 0.010907660185934254,
          "is_forcing": false,
          "is_critical": false
        },
        "themes": [
          {
            "theme": "threat_created",
            "squares": [
              "f3"
            ],
            "pieces": [
              "N@f3",
              "b@g4"
            ],
            "confidence": 0.8,
            "evidence": "the move now attacks the defended N@f3"
          },
          {
            "theme": "x_ray",
            "squares": [
              "g4",
              "f3",
              "d1"
            ],
            "pieces": [
              "b@g4"
            ],
            "confidence": 0.6,
            "evidence": "b@g4 sees through N@f3 to the valuable Q@d1 behind it"
          },
          {
            "theme": "weakens_opponent_king",
            "squares": [
              "e1"
            ],
            "pieces": [
              "K@e1"
            ],
            "confidence": 0.7,
            "evidence": "opponent king safety drops from 1.00 to 0.00"
          },
          {
            "theme": "bishop_pair",
            "squares": [
              "g4",
              "f8"
            ],
            "pieces": [
              "b@g4",
              "b@f8"
            ],
            "confidence": 1.0,
            "evidence": "the mover owns both bishops"
          },
          {
            "theme": "develops_piece",
            "squares": [
              "c8",
              "g4"
            ],
            "pieces": [
              "b@g4"
            ],
            "confidence": 1.0,
            "evidence": "b@g4 develops off the back rank"
          }
        ],
        "positional_delta": {
          "material": 0.0,
          "mobility": 18.0,
          "king_safety": 0.0,
          "pawn_structure": 0.0,
          "space": 0.0,
          "activity": 5.0
        },
        "intent": [
          {
            "tag": "improves_piece",
            "evidence": "the b moves toward the centre",
            "moves": [],
            "confidence": 0.7
          },
          {
            "tag": "develops",
            "evidence": "develops the b to g4",
            "moves": [],
            "confidence": 1.0
          },
          {
            "tag": "attacks_king",
            "evidence": "pressure on the enemy king rises",
            "moves": [],
            "confidence": 0.7
          }
        ],
        "pv": [
          "d4e5",
          "b8d7",
          "e5d6",
          "f8d6",
          "h2h3",
          "g4h5",
          "g2g4"
        ],
        "fen_after": "rn1qkbnr/ppp2ppp/3p4/4p3/3PP1b1/5N2/PPP2PPP/RNBQKB1R w KQkq - 1 4",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 94866,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 6,
        "fen_before": "rn1qkbnr/ppp2ppp/3p4/4p3/3PP1b1/5N2/PPP2PPP/RNBQKB1R w KQkq - 1 4",
        "move_uci": "d4e5",
        "move_san": "dxe5",
        "quality": {
          "label": "excellent",
          "eval_before_cp": 95.0,
          "eval_after_cp": 82.0,
          "win_prob_before": 0.5865684965842631,
          "win_prob_after": 0.5749143902876699,
          "loss_cp": 13.0,
          "loss_wp": 0.011654106296593247,
          "best_move": "c1e3",
          "best_move_san": "Be3",
          "best_move_cp": 95.0,
          "best_move_wp": 0.5865684965842631,
          "rank": null,
          "n_lines": 3,
          "played_in_multipv": false,
          "is_only_move": false,
          "gap_to_second_wp": 0.0035761994675658215,
          "sharpness": 0.013454802682380973,
          "is_forcing": true,
          "is_critical": false
        },
        "themes": [
          {
            "theme": "x_ray",
            "squares": [
              "d1",
              "d6",
              "d8"
            ],
            "pieces": [
              "Q@d1"
            ],
            "confidence": 0.6,
            "evidence": "Q@d1 sees through p@d6 to the valuable q@d8 behind it"
          },
          {
            "theme": "capture",
            "squares": [
              "d4",
              "e5"
            ],
            "pieces": [
              "P@e5"
            ],
            "confidence": 1.0,
            "evidence": "takes the p@e5"
          },
          {
            "theme": "weakens_opponent_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 0.7,
            "evidence": "opponent king safety drops from 2.00 to 0.00"
          },
          {
            "theme": "doubled_pawn",
            "squares": [
              "e4"
            ],
            "pieces": [
              "P@e4"
            ],
            "confidence": 1.0,
            "evidence": "doubled pawns on the e-file"
          },
          {
            "theme": "backward_pawn",
            "squares": [
              "e5"
            ],
            "pieces": [
              "P@e5"
            ],
            "confidence": 0.7,
            "evidence": "backward pawn on e5"
          },
          {
            "theme": "pawn_island",
            "squares": [],
            "pieces": [],
            "confidence": 0.7,
            "evidence": "pawn island count changes from 1 to 2"
          },
          {
            "theme": "pawn_break",
            "squares": [
              "e5"
            ],
            "pieces": [
              "P@e5"
            ],
            "confidence": 1.0,
            "evidence": "pawn on e5 attacks an enemy pawn"
          },
          {
            "theme": "bishop_pair",
            "squares": [
              "c1",
              "f1"
            ],
            "pieces": [
              "B@c1",
              "B@f1"
            ],
            "confidence": 1.0,
            "evidence": "the mover owns both bishops"
          }
        ],
        "positional_delta": {
          "material": 100.0,
          "mobility": 18.0,
          "king_safety": 0.0,
          "pawn_structure": -40.0,
          "space": 0.0,
          "activity": 0.0
        },
        "intent": [
          {
            "tag": "attacks_king",
            "evidence": "pressure on the enemy king rises",
            "moves": [],
            "confidence": 0.7
          }
        ],
        "pv": [
          "b8d7",
          "h2h3",
          "g4h5",
          "g2g4",
          "h5g6",
          "c1g5",
          "f8e7",
          "g5e7",
          "d8e7",
          "e5d6",
          "e7e4",
          "d1e2"
        ],
        "fen_after": "rn1qkbnr/ppp2ppp/3p4/4P3/4P1b1/5N2/PPP2PPP/RNBQKB1R b KQkq - 0 4",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 89464,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 7,
        "fen_before": "rn1qkbnr/ppp2ppp/3p4/4P3/4P1b1/5N2/PPP2PPP/RNBQKB1R b KQkq - 0 4",
        "move_uci": "g4f3",
        "move_san": "Bxf3",
        "quality": {
          "label": "inaccuracy",
          "eval_before_cp": -82.0,
          "eval_after_cp": -193.0,
          "win_prob_before": 0.42508560971233006,
          "win_prob_after": 0.3294571208942188,
          "loss_cp": 111.0,
          "loss_wp": 0.09562848881811126,
          "best_move": "b8d7",
          "best_move_san": "Nd7",
          "best_move_cp": -82.0,
          "best_move_wp": 0.42508560971233006,
          "rank": null,
          "n_lines": 3,
          "played_in_multipv": false,
          "is_only_move": false,
          "gap_to_second_wp": 0.008077906829027315,
          "sharpness": 0.06655987847072614,
          "is_forcing": true,
          "is_critical": false
        },
        "themes": [
          {
            "theme": "pin",
            "squares": [
              "d1"
            ],
            "pieces": [
              "Q@d1",
              "b@f3"
            ],
            "confidence": 0.6,
            "evidence": "the cheap b@f3 holds the defended Q@d1 in place"
          },
          {
            "theme": "threat_created",
            "squares": [
              "d1"
            ],
            "pieces": [
              "Q@d1",
              "b@f3"
            ],
            "confidence": 0.8,
            "evidence": "the move now attacks the defended Q@d1"
          },
          {
            "theme": "x_ray",
            "squares": [
              "f3",
              "g2",
              "h1"
            ],
            "pieces": [
              "b@f3"
            ],
            "confidence": 0.6,
            "evidence": "b@f3 sees through P@g2 to the valuable R@h1 behind it"
          },
          {
            "theme": "capture",
            "squares": [
              "g4",
              "f3"
            ],
            "pieces": [
              "b@f3"
            ],
            "confidence": 1.0,
            "evidence": "takes the N@f3"
          },
          {
            "theme": "trade",
            "squares": [
              "g4",
              "f3"
            ],
            "pieces": [
              "b@f3"
            ],
            "confidence": 0.8,
            "evidence": "trades the b@g4 for the N@f3"
          },
          {
            "theme": "simplification",
            "squares": [
              "g4",
              "f3"
            ],
            "pieces": [
              "b@f3"
            ],
            "confidence": 0.8,
            "evidence": "trades the b@g4 for the N@f3 and thins the board"
          },
          {
            "theme": "weakens_opponent_king",
            "squares": [
              "e1"
            ],
            "pieces": [
              "K@e1"
            ],
            "confidence": 0.7,
            "evidence": "opponent king safety drops from 0.00 to -1.00"
          },
          {
            "theme": "backward_pawn",
            "squares": [
              "d6"
            ],
            "pieces": [
              "p@d6"
            ],
            "confidence": 0.7,
            "evidence": "backward pawn on d6"
          },
          {
            "theme": "bishop_pair",
            "squares": [
              "f3",
              "f8"
            ],
            "pieces": [
              "b@f3",
              "b@f8"
            ],
            "confidence": 1.0,
            "evidence": "the mover owns both bishops"
          },
          {
            "theme": "controls_center",
            "squares": [],
            "pieces": [],
            "confidence": 0.8,
            "evidence": "central control rises from 1.00 to 2.00"
          }
        ],
        "positional_delta": {
          "material": 320.0,
          "mobility": -6.0,
          "king_safety": 0.0,
          "pawn_structure": 0.0,
          "space": 4.0,
          "activity": 7.5
        },
        "intent": [
          {
            "tag": "improves_piece",
            "evidence": "the b moves toward the centre",
            "moves": [],
            "confidence": 0.7
          },
          {
            "tag": "restricts_opponent",
            "evidence": "opponent mobility drops from 25.0 to 21.0",
            "moves": [],
            "confidence": 0.7
          },
          {
            "tag": "trades_defender",
            "evidence": "the move removes the defender of e5",
            "moves": [],
            "confidence": 0.7
          },
          {
            "tag": "simplifies",
            "evidence": "an even exchange that thins the position",
            "moves": [],
            "confidence": 1.0
          },
          {
            "tag": "attacks_king",
            "evidence": "pressure on the enemy king rises",
            "moves": [],
            "confidence": 0.7
          }
        ],
        "pv": [
          "d1f3",
          "d6e5",
          "f3b3",
          "b8d7",
          "f1c4",
          "d8f6",
          "b3b7",
          "a8b8",
          "b7d5",
          "f8c5",
          "e1g1",
          "g8e7",
          "d5d2",
          "f6c6",
          "d2e2",
          "e8g8",
          "g2g3",
          "d7f6"
        ],
        "fen_after": "rn1qkbnr/ppp2ppp/3p4/4P3/4P3/5b2/PPP2PPP/RNBQKB1R w KQkq - 0 5",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 85093,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 8,
        "fen_before": "rn1qkbnr/ppp2ppp/3p4/4P3/4P3/5b2/PPP2PPP/RNBQKB1R w KQkq - 0 5",
        "move_uci": "d1f3",
        "move_san": "Qxf3",
        "quality": {
          "label": "best",
          "eval_before_cp": 184.0,
          "eval_after_cp": 184.0,
          "win_prob_before": 0.6631811026712696,
          "win_prob_after": 0.6631811026712696,
          "loss_cp": 0.0,
          "loss_wp": 0.0,
          "best_move": "d1f3",
          "best_move_san": "Qxf3",
          "best_move_cp": 184.0,
          "best_move_wp": 0.6631811026712696,
          "rank": 1,
          "n_lines": 3,
          "played_in_multipv": true,
          "is_only_move": false,
          "gap_to_second_wp": 0.055358801743996655,
          "sharpness": 0.458127854338218,
          "is_forcing": true,
          "is_critical": true
        },
        "themes": [
          {
            "theme": "x_ray",
            "squares": [
              "f3",
              "f7",
              "f8"
            ],
            "pieces": [
              "Q@f3"
            ],
            "confidence": 0.6,
            "evidence": "Q@f3 sees through p@f7 to the valuable b@f8 behind it"
          },
          {
            "theme": "capture",
            "squares": [
              "d1",
              "f3"
            ],
            "pieces": [
              "Q@f3"
            ],
            "confidence": 1.0,
            "evidence": "takes the b@f3"
          },
          {
            "theme": "shelters_king",
            "squares": [
              "e1"
            ],
            "pieces": [
              "K@e1"
            ],
            "confidence": 1.0,
            "evidence": "king safety rises from -1.00 to 1.00"
          },
          {
            "theme": "weakens_opponent_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 0.7,
            "evidence": "opponent king safety drops from 0.00 to -1.00"
          },
          {
            "theme": "doubled_pawn",
            "squares": [
              "e4"
            ],
            "pieces": [
              "P@e4"
            ],
            "confidence": 1.0,
            "evidence": "doubled pawns on the e-file"
          },
          {
            "theme": "backward_pawn",
            "squares": [
              "e5"
            ],
            "pieces": [
              "P@e5"
            ],
            "confidence": 0.7,
            "evidence": "backward pawn on e5"
          },
          {
            "theme": "bishop_pair",
            "squares": [
              "c1",
              "f1"
            ],
            "pieces": [
              "B@c1",
              "B@f1"
            ],
            "confidence": 1.0,
            "evidence": "the mover owns both bishops"
          }
        ],
        "positional_delta": {
          "material": 330.0,
          "mobility": 48.0,
          "king_safety": 24.0,
          "pawn_structure": 0.0,
          "space": 0.0,
          "activity": -5.0
        },
        "intent": [
          {
            "tag": "improves_piece",
            "evidence": "the Q moves toward the centre",
            "moves": [],
            "confidence": 0.7
          },
          {
            "tag": "restricts_opponent",
            "evidence": "opponent mobility drops from 19.0 to 13.0",
            "moves": [],
            "confidence": 0.7
          },
          {
            "tag": "attacks_king",
            "evidence": "pressure on the enemy king rises",
            "moves": [],
            "confidence": 0.7
          }
        ],
        "pv": [
          "d1f3",
          "d6e5",
          "f3b3",
          "b8d7",
          "f1c4",
          "d8f6",
          "b3b7",
          "a8b8",
          "b7d5",
          "f8c5",
          "e1g1",
          "g8e7",
          "d5d2",
          "d7b6",
          "c4b5",
          "c7c6",
          "b5a6",
          "e8g8",
          "d2e2"
        ],
        "fen_after": "rn1qkbnr/ppp2ppp/3p4/4P3/4P3/5Q2/PPP2PPP/RNB1KB1R b KQkq - 0 5",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 35155,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 9,
        "fen_before": "rn1qkbnr/ppp2ppp/3p4/4P3/4P3/5Q2/PPP2PPP/RNB1KB1R b KQkq - 0 5",
        "move_uci": "d6e5",
        "move_san": "dxe5",
        "quality": {
          "label": "best",
          "eval_before_cp": -188.0,
          "eval_after_cp": -188.0,
          "win_prob_before": 0.3335369512006218,
          "win_prob_after": 0.3335369512006218,
          "loss_cp": 0.0,
          "loss_wp": 0.0,
          "best_move": "d6e5",
          "best_move_san": "dxe5",
          "best_move_cp": -188.0,
          "best_move_wp": 0.3335369512006218,
          "rank": 1,
          "n_lines": 3,
          "played_in_multipv": true,
          "is_only_move": false,
          "gap_to_second_wp": 0.015366090222054096,
          "sharpness": 0.04416320154167752,
          "is_forcing": true,
          "is_critical": false
        },
        "themes": [
          {
            "theme": "capture",
            "squares": [
              "d6",
              "e5"
            ],
            "pieces": [
              "p@e5"
            ],
            "confidence": 1.0,
            "evidence": "takes the P@e5"
          },
          {
            "theme": "weakens_opponent_king",
            "squares": [
              "e1"
            ],
            "pieces": [
              "K@e1"
            ],
            "confidence": 0.7,
            "evidence": "opponent king safety drops from 1.00 to -2.00"
          },
          {
            "theme": "controls_center",
            "squares": [],
            "pieces": [],
            "confidence": 0.8,
            "evidence": "central control rises from 1.00 to 2.00"
          }
        ],
        "positional_delta": {
          "material": 100.0,
          "mobility": 60.0,
          "king_safety": 0.0,
          "pawn_structure": 20.0,
          "space": 4.0,
          "activity": 0.0
        },
        "intent": [
          {
            "tag": "attacks_king",
            "evidence": "pressure on the enemy king rises",
            "moves": [],
            "confidence": 0.7
          }
        ],
        "pv": [
          "d6e5",
          "f3b3",
          "b8d7",
          "f1c4",
          "d8f6",
          "b3b7",
          "a8b8",
          "b7d5",
          "f8c5",
          "e1g1",
          "g8e7",
          "d5d2",
          "d7b6"
        ],
        "fen_after": "rn1qkbnr/ppp2ppp/8/4p3/4P3/5Q2/PPP2PPP/RNB1KB1R w KQkq - 0 6",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 47185,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 10,
        "fen_before": "rn1qkbnr/ppp2ppp/8/4p3/4P3/5Q2/PPP2PPP/RNB1KB1R w KQkq - 0 6",
        "move_uci": "f1c4",
        "move_san": "Bc4",
        "quality": {
          "label": "good",
          "eval_before_cp": 176.0,
          "eval_after_cp": 125.0,
          "win_prob_before": 0.6565700162843596,
          "win_prob_after": 0.613075853553636,
          "loss_cp": 51.0,
          "loss_wp": 0.043494162730723596,
          "best_move": "f3b3",
          "best_move_san": "Qb3",
          "best_move_cp": 176.0,
          "best_move_wp": 0.6565700162843596,
          "rank": 2,
          "n_lines": 3,
          "played_in_multipv": true,
          "is_only_move": false,
          "gap_to_second_wp": 0.043494162730723596,
          "sharpness": 0.043494162730723596,
          "is_forcing": false,
          "is_critical": false
        },
        "themes": [
          {
            "theme": "x_ray",
            "squares": [
              "c4",
              "f7",
              "g8"
            ],
            "pieces": [
              "B@c4"
            ],
            "confidence": 0.6,
            "evidence": "B@c4 sees through p@f7 to the valuable n@g8 behind it"
          },
          {
            "theme": "weakens_opponent_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 0.7,
            "evidence": "opponent king safety drops from -1.00 to -2.00"
          },
          {
            "theme": "bishop_pair",
            "squares": [
              "c1",
              "c4"
            ],
            "pieces": [
              "B@c1",
              "B@c4"
            ],
            "confidence": 1.0,
            "evidence": "the mover owns both bishops"
          },
          {
            "theme": "develops_piece",
            "squares": [
              "f1",
              "c4"
            ],
            "pieces": [
              "B@c4"
            ],
            "confidence": 1.0,
            "evidence": "B@c4 develops off the back rank"
          }
        ],
        "positional_delta": {
          "material": 0.0,
          "mobility": 30.0,
          "king_safety": 0.0,
          "pawn_structure": 0.0,
          "space": 0.0,
          "activity": 7.5
        },
        "intent": [
          {
            "tag": "improves_piece",
            "evidence": "the B moves toward the centre",
            "moves": [],
            "confidence": 0.7
          },
          {
            "tag": "develops",
            "evidence": "develops the B to c4",
            "moves": [],
            "confidence": 1.0
          },
          {
            "tag": "attacks_king",
            "evidence": "pressure on the enemy king rises",
            "moves": [],
            "confidence": 0.7
          }
        ],
        "pv": [
          "f1c4",
          "d8f6",
          "f3b3",
          "b8d7",
          "b3b7",
          "a8b8",
          "b7a6",
          "f6a6",
          "c4a6",
          "d7c5",
          "a6d3",
          "c5d3",
          "c2d3",
          "f8c5"
        ],
        "fen_after": "rn1qkbnr/ppp2ppp/8/4p3/2B1P3/5Q2/PPP2PPP/RNB1K2R b KQkq - 1 6",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 136375,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 11,
        "fen_before": "rn1qkbnr/ppp2ppp/8/4p3/2B1P3/5Q2/PPP2PPP/RNB1K2R b KQkq - 1 6",
        "move_uci": "g8f6",
        "move_san": "Nf6",
        "quality": {
          "label": "mistake",
          "eval_before_cp": -138.0,
          "eval_after_cp": -291.0,
          "win_prob_before": 0.37563269360828333,
          "win_prob_after": 0.2551207276169529,
          "loss_cp": 153.0,
          "loss_wp": 0.1205119659913304,
          "best_move": "d8d7",
          "best_move_san": "Qd7",
          "best_move_cp": -138.0,
          "best_move_wp": 0.37563269360828333,
          "rank": null,
          "n_lines": 3,
          "played_in_multipv": false,
          "is_only_move": false,
          "gap_to_second_wp": 0.002587124823873743,
          "sharpness": 0.0338613037571705,
          "is_forcing": false,
          "is_critical": true
        },
        "themes": [
          {
            "theme": "interference",
            "squares": [
              "f3",
              "f6",
              "f7"
            ],
            "pieces": [
              "Q@f3",
              "n@f6"
            ],
            "confidence": 0.7,
            "evidence": "n@f6 interposes on the Q@f3's line, denying the capture on f7"
          },
          {
            "theme": "develops_piece",
            "squares": [
              "g8",
              "f6"
            ],
            "pieces": [
              "n@f6"
            ],
            "confidence": 1.0,
            "evidence": "n@f6 develops off the back rank"
          },
          {
            "theme": "controls_center",
            "squares": [],
            "pieces": [],
            "confidence": 0.8,
            "evidence": "central control rises from 2.00 to 3.00"
          }
        ],
        "positional_delta": {
          "material": 0.0,
          "mobility": 6.0,
          "king_safety": 0.0,
          "pawn_structure": 0.0,
          "space": 4.0,
          "activity": 10.0
        },
        "intent": [
          {
            "tag": "improves_piece",
            "evidence": "the n moves toward the centre",
            "moves": [],
            "confidence": 0.7
          },
          {
            "tag": "restricts_opponent",
            "evidence": "opponent mobility drops from 34.0 to 33.0",
            "moves": [],
            "confidence": 0.7
          },
          {
            "tag": "develops",
            "evidence": "develops the n to f6",
            "moves": [],
            "confidence": 1.0
          }
        ],
        "pv": [
          "f3b3",
          "f8e7",
          "c4f7",
          "e8f8",
          "f7d5",
          "b8a6",
          "e1g1",
          "c7c6",
          "d5c4",
          "a6c5"
        ],
        "fen_after": "rn1qkb1r/ppp2ppp/5n2/4p3/2B1P3/5Q2/PPP2PPP/RNB1K2R w KQkq - 2 7",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 53187,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 12,
        "fen_before": "rn1qkb1r/ppp2ppp/5n2/4p3/2B1P3/5Q2/PPP2PPP/RNB1K2R w KQkq - 2 7",
        "move_uci": "f3b3",
        "move_san": "Qb3",
        "quality": {
          "label": "best",
          "eval_before_cp": 256.0,
          "eval_after_cp": 256.0,
          "win_prob_before": 0.7196270640184792,
          "win_prob_after": 0.7196270640184792,
          "loss_cp": 0.0,
          "loss_wp": 0.0,
          "best_move": "f3b3",
          "best_move_san": "Qb3",
          "best_move_cp": 256.0,
          "best_move_wp": 0.7196270640184792,
          "rank": 1,
          "n_lines": 3,
          "played_in_multipv": true,
          "is_only_move": false,
          "gap_to_second_wp": 0.11620193466505324,
          "sharpness": 0.11796553729097448,
          "is_forcing": false,
          "is_critical": false
        },
        "themes": [
          {
            "theme": "x_ray",
            "squares": [
              "b3",
              "b7",
              "b8"
            ],
            "pieces": [
              "Q@b3"
            ],
            "confidence": 0.6,
            "evidence": "Q@b3 sees through p@b7 to the valuable n@b8 behind it"
          },
          {
            "theme": "bishop_pair",
            "squares": [
              "c1",
              "c4"
            ],
            "pieces": [
              "B@c1",
              "B@c4"
            ],
            "confidence": 1.0,
            "evidence": "the mover owns both bishops"
          }
        ],
        "positional_delta": {
          "material": 0.0,
          "mobility": -18.0,
          "king_safety": 0.0,
          "pawn_structure": 0.0,
          "space": -4.0,
          "activity": 2.5
        },
        "intent": [],
        "pv": [
          "f3b3",
          "f8c5",
          "c4f7",
          "e8e7",
          "f7d5",
          "c7c6",
          "b3b7",
          "d8d7",
          "b7d7",
          "e7d7",
          "d5b3",
          "f6e4"
        ],
        "fen_after": "rn1qkb1r/ppp2ppp/5n2/4p3/2B1P3/1Q6/PPP2PPP/RNB1K2R b KQkq - 3 7",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 67855,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 13,
        "fen_before": "rn1qkb1r/ppp2ppp/5n2/4p3/2B1P3/1Q6/PPP2PPP/RNB1K2R b KQkq - 3 7",
        "move_uci": "d8e7",
        "move_san": "Qe7",
        "quality": {
          "label": "good",
          "eval_before_cp": -256.0,
          "eval_after_cp": -299.0,
          "win_prob_before": 0.2803729359815208,
          "win_prob_after": 0.24956344857367777,
          "loss_cp": 43.0,
          "loss_wp": 0.030809487407843034,
          "best_move": "f8c5",
          "best_move_san": "Bc5",
          "best_move_cp": -256.0,
          "best_move_wp": 0.2803729359815208,
          "rank": 2,
          "n_lines": 3,
          "played_in_multipv": true,
          "is_only_move": false,
          "gap_to_second_wp": 0.030809487407843034,
          "sharpness": 0.04830587063447128,
          "is_forcing": false,
          "is_critical": false
        },
        "themes": [
          {
            "theme": "bad_bishop",
            "squares": [
              "f8"
            ],
            "pieces": [
              "b@f8"
            ],
            "confidence": 0.7,
            "evidence": "bishop on f8 is blocked by its own pawns"
          },
          {
            "theme": "controls_center",
            "squares": [],
            "pieces": [],
            "confidence": 0.8,
            "evidence": "central control rises from 3.00 to 4.00"
          }
        ],
        "positional_delta": {
          "material": 0.0,
          "mobility": -42.0,
          "king_safety": 0.0,
          "pawn_structure": 0.0,
          "space": 4.0,
          "activity": -2.5
        },
        "intent": [
          {
            "tag": "improves_piece",
            "evidence": "the q moves toward the centre",
            "moves": [],
            "confidence": 0.7
          }
        ],
        "pv": [
          "d8e7",
          "b3b7",
          "e7b4",
          "b7b4",
          "f8b4",
          "c2c3",
          "b4c5",
          "b1d2",
          "e8e7",
          "f2f3",
          "a7a5",
          "a2a4",
          "f6d7",
          "e1d1",
          "d7b6",
          "d1c2"
        ],
        "fen_after": "rn2kb1r/ppp1qppp/5n2/4p3/2B1P3/1Q6/PPP2PPP/RNB1K2R w KQkq - 4 8",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 20827,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 14,
        "fen_before": "rn2kb1r/ppp1qppp/5n2/4p3/2B1P3/1Q6/PPP2PPP/RNB1K2R w KQkq - 4 8",
        "move_uci": "b1c3",
        "move_san": "Nc3",
        "quality": {
          "label": "good",
          "eval_before_cp": 299.0,
          "eval_after_cp": 237.0,
          "win_prob_before": 0.7504365514263222,
          "win_prob_after": 0.705297423779081,
          "loss_cp": 62.0,
          "loss_wp": 0.04513912764724115,
          "best_move": "b3b7",
          "best_move_san": "Qxb7",
          "best_move_cp": 299.0,
          "best_move_wp": 0.7504365514263222,
          "rank": 2,
          "n_lines": 3,
          "played_in_multipv": true,
          "is_only_move": false,
          "gap_to_second_wp": 0.04513912764724115,
          "sharpness": 0.11576472528128745,
          "is_forcing": false,
          "is_critical": false
        },
        "themes": [
          {
            "theme": "x_ray",
            "squares": [
              "b3",
              "b7",
              "b8"
            ],
            "pieces": [
              "Q@b3"
            ],
            "confidence": 0.6,
            "evidence": "Q@b3 sees through p@b7 to the valuable n@b8 behind it"
          },
          {
            "theme": "bishop_pair",
            "squares": [
              "c1",
              "c4"
            ],
            "pieces": [
              "B@c1",
              "B@c4"
            ],
            "confidence": 1.0,
            "evidence": "the mover owns both bishops"
          },
          {
            "theme": "develops_piece",
            "squares": [
              "b1",
              "c3"
            ],
            "pieces": [
              "N@c3"
            ],
            "confidence": 1.0,
            "evidence": "N@c3 develops off the back rank"
          },
          {
            "theme": "controls_center",
            "squares": [],
            "pieces": [],
            "confidence": 0.8,
            "evidence": "central control rises from 1.00 to 2.00"
          }
        ],
        "positional_delta": {
          "material": 0.0,
          "mobility": -12.0,
          "king_safety": 0.0,
          "pawn_structure": 0.0,
          "space": 4.0,
          "activity": 10.0
        },
        "intent": [
          {
            "tag": "improves_piece",
            "evidence": "the N moves toward the centre",
            "moves": [],
            "confidence": 0.7
          },
          {
            "tag": "develops",
            "evidence": "develops the N to c3",
            "moves": [],
            "confidence": 1.0
          }
        ],
        "pv": [
          "b1c3",
          "c7c6",
          "c1g5",
          "e7c7",
          "e1c1",
          "b7b5",
          "c3b5",
          "c6b5",
          "c4b5",
          "b8c6",
          "d1d3",
          "a7a6"
        ],
        "fen_after": "rn2kb1r/ppp1qppp/5n2/4p3/2B1P3/1QN5/PPP2PPP/R1B1K2R b KQkq - 5 8",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 68756,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 15,
        "fen_before": "rn2kb1r/ppp1qppp/5n2/4p3/2B1P3/1QN5/PPP2PPP/R1B1K2R b KQkq - 5 8",
        "move_uci": "c7c6",
        "move_san": "c6",
        "quality": {
          "label": "best",
          "eval_before_cp": -235.0,
          "eval_after_cp": -235.0,
          "win_prob_before": 0.29623554941924907,
          "win_prob_after": 0.29623554941924907,
          "loss_cp": 0.0,
          "loss_wp": 0.0,
          "best_move": "c7c6",
          "best_move_san": "c6",
          "best_move_cp": -235.0,
          "best_move_wp": 0.29623554941924907,
          "rank": 1,
          "n_lines": 3,
          "played_in_multipv": true,
          "is_only_move": false,
          "gap_to_second_wp": 0.06351164618120678,
          "sharpness": 0.07640180985797873,
          "is_forcing": false,
          "is_critical": false
        },
        "themes": [
          {
            "theme": "bad_bishop",
            "squares": [
              "f8"
            ],
            "pieces": [
              "b@f8"
            ],
            "confidence": 0.7,
            "evidence": "bishop on f8 is blocked by its own pawns"
          }
        ],
        "positional_delta": {
          "material": 0.0,
          "mobility": 0.0,
          "king_safety": 0.0,
          "pawn_structure": 0.0,
          "space": 0.0,
          "activity": 0.0
        },
        "intent": [],
        "pv": [
          "c7c6",
          "c1g5",
          "e7c7",
          "g5f6",
          "g7f6",
          "e1g1",
          "f8g7",
          "a2a4",
          "e8g8"
        ],
        "fen_after": "rn2kb1r/pp2qppp/2p2n2/4p3/2B1P3/1QN5/PPP2PPP/R1B1K2R w KQkq - 0 9",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 72856,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 16,
        "fen_before": "rn2kb1r/pp2qppp/2p2n2/4p3/2B1P3/1QN5/PPP2PPP/R1B1K2R w KQkq - 0 9",
        "move_uci": "c1g5",
        "move_san": "Bg5",
        "quality": {
          "label": "best",
          "eval_before_cp": 244.0,
          "eval_after_cp": 244.0,
          "win_prob_before": 0.7106262503410556,
          "win_prob_after": 0.7106262503410556,
          "loss_cp": 0.0,
          "loss_wp": 0.0,
          "best_move": "c1g5",
          "best_move_san": "Bg5",
          "best_move_cp": 244.0,
          "best_move_wp": 0.7106262503410556,
          "rank": 1,
          "n_lines": 3,
          "played_in_multipv": true,
          "is_only_move": false,
          "gap_to_second_wp": 0.017720415933844325,
          "sharpness": 0.04826811452388946,
          "is_forcing": false,
          "is_critical": false
        },
        "themes": [
          {
            "theme": "threat_created",
            "squares": [
              "f6"
            ],
            "pieces": [
              "n@f6",
              "B@g5"
            ],
            "confidence": 0.8,
            "evidence": "the move now attacks the defended n@f6"
          },
          {
            "theme": "x_ray",
            "squares": [
              "g5",
              "f6",
              "e7"
            ],
            "pieces": [
              "B@g5"
            ],
            "confidence": 0.6,
            "evidence": "B@g5 sees through n@f6 to the valuable q@e7 behind it"
          },
          {
            "theme": "weakens_opponent_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 0.7,
            "evidence": "opponent king safety drops from -1.00 to -2.00"
          },
          {
            "theme": "bishop_pair",
            "squares": [
              "c4",
              "g5"
            ],
            "pieces": [
              "B@c4",
              "B@g5"
            ],
            "confidence": 1.0,
            "evidence": "the mover owns both bishops"
          },
          {
            "theme": "develops_piece",
            "squares": [
              "c1",
              "g5"
            ],
            "pieces": [
              "B@g5"
            ],
            "confidence": 1.0,
            "evidence": "B@g5 develops off the back rank"
          }
        ],
        "positional_delta": {
          "material": 0.0,
          "mobility": 24.0,
          "king_safety": 0.0,
          "pawn_structure": 0.0,
          "space": 0.0,
          "activity": 5.0
        },
        "intent": [
          {
            "tag": "improves_piece",
            "evidence": "the B moves toward the centre",
            "moves": [],
            "confidence": 0.7
          },
          {
            "tag": "develops",
            "evidence": "develops the B to g5",
            "moves": [],
            "confidence": 1.0
          },
          {
            "tag": "attacks_king",
            "evidence": "pressure on the enemy king rises",
            "moves": [],
            "confidence": 0.7
          }
        ],
        "pv": [
          "c1g5",
          "e7c7",
          "e1c1",
          "b7b5",
          "g5f6",
          "b5c4",
          "f6e5",
          "c4b3",
          "e5c7",
          "b8a6",
          "c7g3",
          "b3a2",
          "c3a2",
          "a6c5"
        ],
        "fen_after": "rn2kb1r/pp2qppp/2p2n2/4p1B1/2B1P3/1QN5/PPP2PPP/R3K2R b KQkq - 1 9",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 85021,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 17,
        "fen_before": "rn2kb1r/pp2qppp/2p2n2/4p1B1/2B1P3/1QN5/PPP2PPP/R3K2R b KQkq - 1 9",
        "move_uci": "b7b5",
        "move_san": "b5",
        "quality": {
          "label": "mistake",
          "eval_before_cp": -262.0,
          "eval_after_cp": -459.0,
          "win_prob_before": 0.2759371730995885,
          "win_prob_after": 0.15576601396962686,
          "loss_cp": 197.0,
          "loss_wp": 0.12017115912996162,
          "best_move": "b8a6",
          "best_move_san": "Na6",
          "best_move_cp": -262.0,
          "best_move_wp": 0.2759371730995885,
          "rank": null,
          "n_lines": 3,
          "played_in_multipv": false,
          "is_only_move": false,
          "gap_to_second_wp": 0.0,
          "sharpness": 0.025683503244119388,
          "is_forcing": false,
          "is_critical": true
        },
        "themes": [
          {
            "theme": "pin",
            "squares": [
              "c4"
            ],
            "pieces": [
              "B@c4",
              "p@b5"
            ],
            "confidence": 0.6,
            "evidence": "the cheap p@b5 holds the defended B@c4 in place"
          },
          {
            "theme": "threat_created",
            "squares": [
              "c4"
            ],
            "pieces": [
              "B@c4",
              "p@b5"
            ],
            "confidence": 0.8,
            "evidence": "the move now attacks the defended B@c4"
          },
          {
            "theme": "interference",
            "squares": [
              "b3",
              "b5",
              "b7"
            ],
            "pieces": [
              "Q@b3",
              "p@b5"
            ],
            "confidence": 0.7,
            "evidence": "p@b5 interposes on the Q@b3's line, denying the capture on b7"
          },
          {
            "theme": "bad_bishop",
            "squares": [
              "f8"
            ],
            "pieces": [
              "b@f8"
            ],
            "confidence": 0.7,
            "evidence": "bishop on f8 is blocked by its own pawns"
          }
        ],
        "positional_delta": {
          "material": 0.0,
          "mobility": 6.0,
          "king_safety": 0.0,
          "pawn_structure": 0.0,
          "space": 0.0,
          "activity": 0.0
        },
        "intent": [
          {
            "tag": "restricts_opponent",
            "evidence": "opponent mobility drops from 32.0 to 29.0",
            "moves": [],
            "confidence": 0.7
          }
        ],
        "pv": [
          "c3b5",
          "e7b4",
          "b3b4",
          "f8b4",
          "c2c3",
          "c6b5",
          "c4b5",
          "e8e7",
          "c3b4",
          "h8c8",
          "a1d1",
          "c8c2",
          "e1g1",
          "c2b2"
        ],
        "fen_after": "rn2kb1r/p3qppp/2p2n2/1p2p1B1/2B1P3/1QN5/PPP2PPP/R3K2R w KQkq - 0 10",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 60405,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 18,
        "fen_before": "rn2kb1r/p3qppp/2p2n2/1p2p1B1/2B1P3/1QN5/PPP2PPP/R3K2R w KQkq - 0 10",
        "move_uci": "c3b5",
        "move_san": "Nxb5",
        "quality": {
          "label": "great",
          "eval_before_cp": 446.0,
          "eval_after_cp": 446.0,
          "win_prob_before": 0.837835112999932,
          "win_prob_after": 0.837835112999932,
          "loss_cp": 0.0,
          "loss_wp": 0.0,
          "best_move": "c3b5",
          "best_move_san": "Nxb5",
          "best_move_cp": 446.0,
          "best_move_wp": 0.837835112999932,
          "rank": 1,
          "n_lines": 3,
          "played_in_multipv": true,
          "is_only_move": true,
          "gap_to_second_wp": 0.22650758814917937,
          "sharpness": 0.2611220120439859,
          "is_forcing": true,
          "is_critical": true
        },
        "themes": [
          {
            "theme": "x_ray",
            "squares": [
              "g5",
              "f6",
              "e7"
            ],
            "pieces": [
              "B@g5"
            ],
            "confidence": 0.6,
            "evidence": "B@g5 sees through n@f6 to the valuable q@e7 behind it"
          },
          {
            "theme": "capture",
            "squares": [
              "c3",
              "b5"
            ],
            "pieces": [
              "N@b5"
            ],
            "confidence": 1.0,
            "evidence": "takes the p@b5"
          },
          {
            "theme": "sacrifice",
            "squares": [
              "c3",
              "b5"
            ],
            "pieces": [
              "N@b5"
            ],
            "confidence": 0.8,
            "evidence": "gives up the N@c3 for the p@b5"
          },
          {
            "theme": "weakens_opponent_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 0.7,
            "evidence": "opponent king safety drops from -2.00 to -3.00"
          },
          {
            "theme": "bishop_pair",
            "squares": [
              "c4",
              "g5"
            ],
            "pieces": [
              "B@c4",
              "B@g5"
            ],
            "confidence": 1.0,
            "evidence": "the mover owns both bishops"
          }
        ],
        "positional_delta": {
          "material": 100.0,
          "mobility": 24.0,
          "king_safety": 0.0,
          "pawn_structure": 0.0,
          "space": 0.0,
          "activity": -5.0
        },
        "intent": [
          {
            "tag": "attacks_king",
            "evidence": "pressure on the enemy king rises",
            "moves": [],
            "confidence": 0.7
          }
        ],
        "pv": [
          "c3b5",
          "b8a6",
          "e1c1",
          "a6c5",
          "b3f3",
          "e7b7",
          "b5d6",
          "f8d6",
          "d1d6",
          "c5e4",
          "g5f6"
        ],
        "fen_after": "rn2kb1r/p3qppp/2p2n2/1N2p1B1/2B1P3/1Q6/PPP2PPP/R3K2R b KQkq - 0 10",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 46710,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 19,
        "fen_before": "rn2kb1r/p3qppp/2p2n2/1N2p1B1/2B1P3/1Q6/PPP2PPP/R3K2R b KQkq - 0 10",
        "move_uci": "c6b5",
        "move_san": "cxb5",
        "quality": {
          "label": "inaccuracy",
          "eval_before_cp": -433.0,
          "eval_after_cp": -589.0,
          "win_prob_before": 0.16877407540701395,
          "win_prob_after": 0.10259250923752879,
          "loss_cp": 156.0,
          "loss_wp": 0.06618156616948516,
          "best_move": "e7b4",
          "best_move_san": "Qb4+",
          "best_move_cp": -433.0,
          "best_move_wp": 0.16877407540701395,
          "rank": null,
          "n_lines": 3,
          "played_in_multipv": false,
          "is_only_move": false,
          "gap_to_second_wp": 0.02788210902804497,
          "sharpness": 0.03486334048077472,
          "is_forcing": true,
          "is_critical": false
        },
        "themes": [
          {
            "theme": "pin",
            "squares": [
              "c4"
            ],
            "pieces": [
              "B@c4",
              "p@b5"
            ],
            "confidence": 0.6,
            "evidence": "the cheap p@b5 holds the defended B@c4 in place"
          },
          {
            "theme": "threat_created",
            "squares": [
              "c4"
            ],
            "pieces": [
              "B@c4",
              "p@b5"
            ],
            "confidence": 0.8,
            "evidence": "the move now attacks the defended B@c4"
          },
          {
            "theme": "capture",
            "squares": [
              "c6",
              "b5"
            ],
            "pieces": [
              "p@b5"
            ],
            "confidence": 1.0,
            "evidence": "takes the N@b5"
          },
          {
            "theme": "shelters_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 1.0,
            "evidence": "king safety rises from -3.00 to -2.00"
          },
          {
            "theme": "pawn_island",
            "squares": [],
            "pieces": [],
            "confidence": 0.7,
            "evidence": "pawn island count changes from 3 to 2"
          },
          {
            "theme": "bad_bishop",
            "squares": [
              "f8"
            ],
            "pieces": [
              "b@f8"
            ],
            "confidence": 0.7,
            "evidence": "bishop on f8 is blocked by its own pawns"
          }
        ],
        "positional_delta": {
          "material": 320.0,
          "mobility": 6.0,
          "king_safety": 12.0,
          "pawn_structure": 30.0,
          "space": 0.0,
          "activity": 0.0
        },
        "intent": [
          {
            "tag": "restricts_opponent",
            "evidence": "opponent mobility drops from 33.0 to 29.0",
            "moves": [],
            "confidence": 0.7
          }
        ],
        "pv": [
          "c4b5",
          "b8d7",
          "e1c1",
          "e7e6",
          "g5f6",
          "g7f6",
          "d1d7",
          "e6b3",
          "a2b3",
          "f8c5",
          "d7d5",
          "e8f8",
          "d5c5"
        ],
        "fen_after": "rn2kb1r/p3qppp/5n2/1p2p1B1/2B1P3/1Q6/PPP2PPP/R3K2R w KQkq - 0 11",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 35153,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 20,
        "fen_before": "rn2kb1r/p3qppp/5n2/1p2p1B1/2B1P3/1Q6/PPP2PPP/R3K2R w KQkq - 0 11",
        "move_uci": "c4b5",
        "move_san": "Bxb5+",
        "quality": {
          "label": "great",
          "eval_before_cp": 618.0,
          "eval_after_cp": 618.0,
          "win_prob_before": 0.906829680630278,
          "win_prob_after": 0.906829680630278,
          "loss_cp": 0.0,
          "loss_wp": 0.0,
          "best_move": "c4b5",
          "best_move_san": "Bxb5+",
          "best_move_cp": 618.0,
          "best_move_wp": 0.906829680630278,
          "rank": 1,
          "n_lines": 3,
          "played_in_multipv": true,
          "is_only_move": true,
          "gap_to_second_wp": 0.2815992020533614,
          "sharpness": 0.5600710537309631,
          "is_forcing": true,
          "is_critical": true
        },
        "themes": [
          {
            "theme": "trapped_piece",
            "squares": [
              "f6"
            ],
            "pieces": [
              "n@f6"
            ],
            "confidence": 0.7,
            "evidence": "n@f6 is attacked and every square it can reach is covered too"
          },
          {
            "theme": "x_ray",
            "squares": [
              "g5",
              "f6",
              "e7"
            ],
            "pieces": [
              "B@g5"
            ],
            "confidence": 0.6,
            "evidence": "B@g5 sees through n@f6 to the valuable q@e7 behind it"
          },
          {
            "theme": "capture",
            "squares": [
              "c4",
              "b5"
            ],
            "pieces": [
              "B@b5"
            ],
            "confidence": 1.0,
            "evidence": "takes the p@b5"
          },
          {
            "theme": "weakens_opponent_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 0.7,
            "evidence": "opponent king safety drops from -2.00 to -4.00"
          },
          {
            "theme": "passed_pawn",
            "squares": [
              "c2"
            ],
            "pieces": [
              "P@c2"
            ],
            "confidence": 1.0,
            "evidence": "passed pawn on c2"
          },
          {
            "theme": "creates_passed_pawn",
            "squares": [
              "c2"
            ],
            "pieces": [
              "P@c2"
            ],
            "confidence": 1.0,
            "evidence": "the move creates a passed pawn on c2"
          },
          {
            "theme": "bishop_pair",
            "squares": [
              "b5",
              "g5"
            ],
            "pieces": [
              "B@b5",
              "B@g5"
            ],
            "confidence": 1.0,
            "evidence": "the mover owns both bishops"
          }
        ],
        "positional_delta": {
          "material": 100.0,
          "mobility": 30.0,
          "king_safety": 0.0,
          "pawn_structure": 25.0,
          "space": 0.0,
          "activity": -2.5
        },
        "intent": [
          {
            "tag": "attacks_king",
            "evidence": "Bxb5+ gives check",
            "moves": [],
            "confidence": 1.0
          }
        ],
        "pv": [
          "c4b5",
          "b8d7",
          "e1c1",
          "a8d8",
          "d1d5",
          "a7a6",
          "b5a4",
          "a6a5",
          "h1d1",
          "f6d5",
          "g5e7"
        ],
        "fen_after": "rn2kb1r/p3qppp/5n2/1B2p1B1/4P3/1Q6/PPP2PPP/R3K2R b KQkq - 0 11",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 17299,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 21,
        "fen_before": "rn2kb1r/p3qppp/5n2/1B2p1B1/4P3/1Q6/PPP2PPP/R3K2R b KQkq - 0 11",
        "move_uci": "b8d7",
        "move_san": "Nbd7",
        "quality": {
          "label": "best",
          "eval_before_cp": -587.0,
          "eval_after_cp": -587.0,
          "win_prob_before": 0.10327249441731556,
          "win_prob_after": 0.10327249441731556,
          "loss_cp": 0.0,
          "loss_wp": 0.0,
          "best_move": "b8d7",
          "best_move_san": "Nbd7",
          "best_move_cp": -587.0,
          "best_move_wp": 0.10327249441731556,
          "rank": 1,
          "n_lines": 3,
          "played_in_multipv": true,
          "is_only_move": false,
          "gap_to_second_wp": 0.03574614683070318,
          "sharpness": 0.051009919699819904,
          "is_forcing": false,
          "is_critical": false
        },
        "themes": [
          {
            "theme": "interference",
            "squares": [
              "b5",
              "d7",
              "e8"
            ],
            "pieces": [
              "B@b5",
              "n@d7"
            ],
            "confidence": 0.7,
            "evidence": "n@d7 interposes on the B@b5's line, denying the capture on e8"
          },
          {
            "theme": "shelters_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 1.0,
            "evidence": "king safety rises from -4.00 to -3.00"
          },
          {
            "theme": "isolated_pawn",
            "squares": [
              "a7"
            ],
            "pieces": [
              "p@a7"
            ],
            "confidence": 1.0,
            "evidence": "isolated pawn on a7"
          },
          {
            "theme": "bad_bishop",
            "squares": [
              "f8"
            ],
            "pieces": [
              "b@f8"
            ],
            "confidence": 0.7,
            "evidence": "bishop on f8 is blocked by its own pawns"
          },
          {
            "theme": "develops_piece",
            "squares": [
              "b8",
              "d7"
            ],
            "pieces": [
              "n@d7"
            ],
            "confidence": 1.0,
            "evidence": "n@d7 develops off the back rank"
          }
        ],
        "positional_delta": {
          "material": 0.0,
          "mobility": -6.0,
          "king_safety": 12.0,
          "pawn_structure": 0.0,
          "space": 0.0,
          "activity": 5.0
        },
        "intent": [
          {
            "tag": "improves_piece",
            "evidence": "the n moves toward the centre",
            "moves": [],
            "confidence": 0.7
          },
          {
            "tag": "restricts_opponent",
            "evidence": "opponent mobility drops from 34.0 to 33.0",
            "moves": [],
            "confidence": 0.7
          },
          {
            "tag": "develops",
            "evidence": "develops the n to d7",
            "moves": [],
            "confidence": 1.0
          }
        ],
        "pv": [
          "b8d7",
          "e1c1",
          "a8d8",
          "d1d5",
          "a7a6",
          "b5a4",
          "f6d5",
          "g5e7",
          "d5e7",
          "b3c3",
          "e7c8",
          "c3e5",
          "f8e7",
          "e5g7"
        ],
        "fen_after": "r3kb1r/p2nqppp/5n2/1B2p1B1/4P3/1Q6/PPP2PPP/R3K2R w KQkq - 1 12",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 95442,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 22,
        "fen_before": "r3kb1r/p2nqppp/5n2/1B2p1B1/4P3/1Q6/PPP2PPP/R3K2R w KQkq - 1 12",
        "move_uci": "e1c1",
        "move_san": "O-O-O",
        "quality": {
          "label": "best",
          "eval_before_cp": 575.0,
          "eval_after_cp": 575.0,
          "win_prob_before": 0.8925633384935145,
          "win_prob_after": 0.8925633384935145,
          "loss_cp": 0.0,
          "loss_wp": 0.0,
          "best_move": "e1c1",
          "best_move_san": "O-O-O",
          "best_move_cp": 575.0,
          "best_move_wp": 0.8925633384935145,
          "rank": 1,
          "n_lines": 3,
          "played_in_multipv": true,
          "is_only_move": false,
          "gap_to_second_wp": 0.09881959968736809,
          "sharpness": 0.21233390162532306,
          "is_forcing": false,
          "is_critical": false
        },
        "themes": [
          {
            "theme": "pin",
            "squares": [
              "d7"
            ],
            "pieces": [
              "n@d7"
            ],
            "confidence": 1.0,
            "evidence": "n@d7 cannot move without exposing its own king"
          },
          {
            "theme": "x_ray",
            "squares": [
              "g5",
              "f6",
              "e7"
            ],
            "pieces": [
              "B@g5"
            ],
            "confidence": 0.6,
            "evidence": "B@g5 sees through n@f6 to the valuable q@e7 behind it"
          },
          {
            "theme": "shelters_king",
            "squares": [
              "c1"
            ],
            "pieces": [
              "K@c1"
            ],
            "confidence": 1.0,
            "evidence": "king safety rises from 1.00 to 2.00"
          },
          {
            "theme": "weakens_opponent_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 0.7,
            "evidence": "opponent king safety drops from -3.00 to -4.00"
          },
          {
            "theme": "passed_pawn",
            "squares": [
              "c2"
            ],
            "pieces": [
              "P@c2"
            ],
            "confidence": 1.0,
            "evidence": "passed pawn on c2"
          },
          {
            "theme": "bishop_pair",
            "squares": [
              "b5",
              "g5"
            ],
            "pieces": [
              "B@b5",
              "B@g5"
            ],
            "confidence": 1.0,
            "evidence": "the mover owns both bishops"
          },
          {
            "theme": "controls_center",
            "squares": [],
            "pieces": [],
            "confidence": 0.8,
            "evidence": "central control rises from 1.00 to 2.00"
          }
        ],
        "positional_delta": {
          "material": 0.0,
          "mobility": 36.0,
          "king_safety": 12.0,
          "pawn_structure": 0.0,
          "space": 4.0,
          "activity": 5.0
        },
        "intent": [
          {
            "tag": "castles",
            "evidence": "the move castles",
            "moves": [],
            "confidence": 1.0
          },
          {
            "tag": "attacks_king",
            "evidence": "pressure on the enemy king rises",
            "moves": [],
            "confidence": 0.7
          }
        ],
        "pv": [
          "e1c1",
          "a8d8",
          "d1d5",
          "f6d5",
          "g5e7",
          "d5e7",
          "h1d1",
          "e7c8"
        ],
        "fen_after": "r3kb1r/p2nqppp/5n2/1B2p1B1/4P3/1Q6/PPP2PPP/2KR3R b kq - 2 12",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 47800,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 23,
        "fen_before": "r3kb1r/p2nqppp/5n2/1B2p1B1/4P3/1Q6/PPP2PPP/2KR3R b kq - 2 12",
        "move_uci": "a8d8",
        "move_san": "Rd8",
        "quality": {
          "label": "good",
          "eval_before_cp": -631.0,
          "eval_after_cp": -742.0,
          "win_prob_before": 0.08920404718859541,
          "win_prob_after": 0.06110537842022126,
          "loss_cp": 111.0,
          "loss_wp": 0.02809866876837415,
          "best_move": "e7e6",
          "best_move_san": "Qe6",
          "best_move_cp": -631.0,
          "best_move_wp": 0.08920404718859541,
          "rank": 3,
          "n_lines": 3,
          "played_in_multipv": true,
          "is_only_move": false,
          "gap_to_second_wp": 0.016394862797465895,
          "sharpness": 0.02809866876837415,
          "is_forcing": false,
          "is_critical": false
        },
        "themes": [
          {
            "theme": "isolated_pawn",
            "squares": [
              "a7"
            ],
            "pieces": [
              "p@a7"
            ],
            "confidence": 1.0,
            "evidence": "isolated pawn on a7"
          },
          {
            "theme": "rook_open_file",
            "squares": [
              "d8"
            ],
            "pieces": [
              "r@d8"
            ],
            "confidence": 1.0,
            "evidence": "rook on the open d-file"
          },
          {
            "theme": "bad_bishop",
            "squares": [
              "f8"
            ],
            "pieces": [
              "b@f8"
            ],
            "confidence": 0.7,
            "evidence": "bishop on f8 is blocked by its own pawns"
          }
        ],
        "positional_delta": {
          "material": 0.0,
          "mobility": -6.0,
          "king_safety": 0.0,
          "pawn_structure": 0.0,
          "space": 0.0,
          "activity": 5.0
        },
        "intent": [],
        "pv": [
          "a8d8",
          "d1d7",
          "d8d7",
          "h1d1",
          "e7c5",
          "g5f6",
          "f8d6",
          "f6g5"
        ],
        "fen_after": "3rkb1r/p2nqppp/5n2/1B2p1B1/4P3/1Q6/PPP2PPP/2KR3R w k - 3 13",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 59560,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 24,
        "fen_before": "3rkb1r/p2nqppp/5n2/1B2p1B1/4P3/1Q6/PPP2PPP/2KR3R w k - 3 13",
        "move_uci": "d1d7",
        "move_san": "Rxd7",
        "quality": {
          "label": "best",
          "eval_before_cp": 728.0,
          "eval_after_cp": 728.0,
          "win_prob_before": 0.9358693959358768,
          "win_prob_after": 0.9358693959358768,
          "loss_cp": 0.0,
          "loss_wp": 0.0,
          "best_move": "d1d7",
          "best_move_san": "Rxd7",
          "best_move_cp": 728.0,
          "best_move_wp": 0.9358693959358768,
          "rank": 1,
          "n_lines": 3,
          "played_in_multipv": true,
          "is_only_move": false,
          "gap_to_second_wp": 0.03316350103705956,
          "sharpness": 0.0719297717399171,
          "is_forcing": true,
          "is_critical": false
        },
        "themes": [
          {
            "theme": "pin",
            "squares": [
              "e7"
            ],
            "pieces": [
              "q@e7",
              "R@d7"
            ],
            "confidence": 0.6,
            "evidence": "the cheap R@d7 holds the defended q@e7 in place"
          },
          {
            "theme": "skewer",
            "squares": [
              "d7",
              "e7",
              "f7"
            ],
            "pieces": [
              "R@d7"
            ],
            "confidence": 0.7,
            "evidence": "R@d7 skewers the valuable q@e7, which must step aside and let p@f7 fall"
          },
          {
            "theme": "threat_created",
            "squares": [
              "e7"
            ],
            "pieces": [
              "q@e7",
              "R@d7"
            ],
            "confidence": 0.8,
            "evidence": "the move now attacks the defended q@e7"
          },
          {
            "theme": "x_ray",
            "squares": [
              "g5",
              "f6",
              "e7"
            ],
            "pieces": [
              "B@g5"
            ],
            "confidence": 0.6,
            "evidence": "B@g5 sees through n@f6 to the valuable q@e7 behind it"
          },
          {
            "theme": "capture",
            "squares": [
              "d1",
              "d7"
            ],
            "pieces": [
              "R@d7"
            ],
            "confidence": 1.0,
            "evidence": "takes the n@d7"
          },
          {
            "theme": "sacrifice",
            "squares": [
              "d1",
              "d7"
            ],
            "pieces": [
              "R@d7"
            ],
            "confidence": 0.8,
            "evidence": "gives up the R@d1 for the n@d7"
          },
          {
            "theme": "weakens_opponent_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 0.7,
            "evidence": "opponent king safety drops from -4.00 to -6.00"
          },
          {
            "theme": "passed_pawn",
            "squares": [
              "c2"
            ],
            "pieces": [
              "P@c2"
            ],
            "confidence": 1.0,
            "evidence": "passed pawn on c2"
          },
          {
            "theme": "rook_open_file",
            "squares": [
              "d7"
            ],
            "pieces": [
              "R@d7"
            ],
            "confidence": 1.0,
            "evidence": "rook on the open d-file"
          },
          {
            "theme": "rook_seventh",
            "squares": [
              "d7"
            ],
            "pieces": [
              "R@d7"
            ],
            "confidence": 1.0,
            "evidence": "rook reaches the seventh rank on d7"
          },
          {
            "theme": "bishop_pair",
            "squares": [
              "b5",
              "g5"
            ],
            "pieces": [
              "B@b5",
              "B@g5"
            ],
            "confidence": 1.0,
            "evidence": "the mover owns both bishops"
          },
          {
            "theme": "develops_piece",
            "squares": [
              "d1",
              "d7"
            ],
            "pieces": [
              "R@d7"
            ],
            "confidence": 1.0,
            "evidence": "R@d7 develops off the back rank"
          }
        ],
        "positional_delta": {
          "material": 320.0,
          "mobility": 12.0,
          "king_safety": 0.0,
          "pawn_structure": 0.0,
          "space": 0.0,
          "activity": -2.5
        },
        "intent": [
          {
            "tag": "improves_piece",
            "evidence": "the R moves toward the centre",
            "moves": [],
            "confidence": 0.7
          },
          {
            "tag": "trades_defender",
            "evidence": "the move removes the defender of f6",
            "moves": [],
            "confidence": 0.7
          },
          {
            "tag": "develops",
            "evidence": "develops the R to d7",
            "moves": [],
            "confidence": 1.0
          },
          {
            "tag": "attacks_king",
            "evidence": "pressure on the enemy king rises",
            "moves": [],
            "confidence": 0.7
          }
        ],
        "pv": [
          "d1d7",
          "d8d7",
          "h1d1",
          "e7c5",
          "g5f6",
          "f8d6",
          "f6g7",
          "h8g8",
          "b5d7",
          "e8e7",
          "d7f5",
          "g8g7"
        ],
        "fen_after": "3rkb1r/p2Rqppp/5n2/1B2p1B1/4P3/1Q6/PPP2PPP/2K4R b k - 0 13",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 17073,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 25,
        "fen_before": "3rkb1r/p2Rqppp/5n2/1B2p1B1/4P3/1Q6/PPP2PPP/2K4R b k - 0 13",
        "move_uci": "d8d7",
        "move_san": "Rxd7",
        "quality": {
          "label": "best",
          "eval_before_cp": -721.0,
          "eval_after_cp": -721.0,
          "win_prob_before": 0.0656950269019375,
          "win_prob_after": 0.0656950269019375,
          "loss_cp": 0.0,
          "loss_wp": 0.0,
          "best_move": "d8d7",
          "best_move_san": "Rxd7",
          "best_move_cp": -721.0,
          "best_move_wp": 0.0656950269019375,
          "rank": 1,
          "n_lines": 3,
          "played_in_multipv": true,
          "is_only_move": false,
          "gap_to_second_wp": 0.019459565516614055,
          "sharpness": 0.026519048913106608,
          "is_forcing": true,
          "is_critical": false
        },
        "themes": [
          {
            "theme": "capture",
            "squares": [
              "d8",
              "d7"
            ],
            "pieces": [
              "r@d7"
            ],
            "confidence": 1.0,
            "evidence": "takes the R@d7"
          },
          {
            "theme": "shelters_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 1.0,
            "evidence": "king safety rises from -6.00 to -3.00"
          },
          {
            "theme": "weakens_opponent_king",
            "squares": [
              "c1"
            ],
            "pieces": [
              "K@c1"
            ],
            "confidence": 0.7,
            "evidence": "opponent king safety drops from 2.00 to -1.00"
          },
          {
            "theme": "isolated_pawn",
            "squares": [
              "a7"
            ],
            "pieces": [
              "p@a7"
            ],
            "confidence": 1.0,
            "evidence": "isolated pawn on a7"
          },
          {
            "theme": "rook_open_file",
            "squares": [
              "d7"
            ],
            "pieces": [
              "r@d7"
            ],
            "confidence": 1.0,
            "evidence": "rook on the open d-file"
          },
          {
            "theme": "bad_bishop",
            "squares": [
              "f8"
            ],
            "pieces": [
              "b@f8"
            ],
            "confidence": 0.7,
            "evidence": "bishop on f8 is blocked by its own pawns"
          },
          {
            "theme": "develops_piece",
            "squares": [
              "d8",
              "d7"
            ],
            "pieces": [
              "r@d7"
            ],
            "confidence": 1.0,
            "evidence": "r@d7 develops off the back rank"
          }
        ],
        "positional_delta": {
          "material": 500.0,
          "mobility": 24.0,
          "king_safety": 36.0,
          "pawn_structure": 0.0,
          "space": 0.0,
          "activity": -2.5
        },
        "intent": [
          {
            "tag": "improves_piece",
            "evidence": "the r moves toward the centre",
            "moves": [],
            "confidence": 0.7
          },
          {
            "tag": "restricts_opponent",
            "evidence": "opponent mobility drops from 41.0 to 31.0",
            "moves": [],
            "confidence": 0.7
          },
          {
            "tag": "develops",
            "evidence": "develops the r to d7",
            "moves": [],
            "confidence": 1.0
          },
          {
            "tag": "attacks_king",
            "evidence": "pressure on the enemy king rises",
            "moves": [],
            "confidence": 0.7
          }
        ],
        "pv": [
          "d8d7",
          "h1d1",
          "e7c5",
          "g5f6",
          "f8d6",
          "b5d7",
          "e8d7",
          "b3f7",
          "d7c6",
          "f6g7",
          "h8b8",
          "a2a4"
        ],
        "fen_after": "4kb1r/p2rqppp/5n2/1B2p1B1/4P3/1Q6/PPP2PPP/2K4R w k - 0 14",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 24913,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 26,
        "fen_before": "4kb1r/p2rqppp/5n2/1B2p1B1/4P3/1Q6/PPP2PPP/2K4R w k - 0 14",
        "move_uci": "h1d1",
        "move_san": "Rd1",
        "quality": {
          "label": "great",
          "eval_before_cp": 716.0,
          "eval_after_cp": 716.0,
          "win_prob_before": 0.9331658819626997,
          "win_prob_after": 0.9331658819626997,
          "loss_cp": 0.0,
          "loss_wp": 0.0,
          "best_move": "h1d1",
          "best_move_san": "Rd1",
          "best_move_cp": 716.0,
          "best_move_wp": 0.9331658819626997,
          "rank": 1,
          "n_lines": 3,
          "played_in_multipv": true,
          "is_only_move": true,
          "gap_to_second_wp": 0.19250759889244495,
          "sharpness": 0.22329738878687122,
          "is_forcing": false,
          "is_critical": true
        },
        "themes": [
          {
            "theme": "pin",
            "squares": [
              "d7"
            ],
            "pieces": [
              "r@d7"
            ],
            "confidence": 1.0,
            "evidence": "r@d7 cannot move without exposing its own king"
          },
          {
            "theme": "threat_created",
            "squares": [
              "d7"
            ],
            "pieces": [
              "r@d7",
              "R@d1"
            ],
            "confidence": 0.8,
            "evidence": "the move now attacks the defended r@d7"
          },
          {
            "theme": "x_ray",
            "squares": [
              "g5",
              "f6",
              "e7"
            ],
            "pieces": [
              "B@g5"
            ],
            "confidence": 0.6,
            "evidence": "B@g5 sees through n@f6 to the valuable q@e7 behind it"
          },
          {
            "theme": "weakens_opponent_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 0.7,
            "evidence": "opponent king safety drops from -3.00 to -4.00"
          },
          {
            "theme": "passed_pawn",
            "squares": [
              "c2"
            ],
            "pieces": [
              "P@c2"
            ],
            "confidence": 1.0,
            "evidence": "passed pawn on c2"
          },
          {
            "theme": "rook_open_file",
            "squares": [
              "d1"
            ],
            "pieces": [
              "R@d1"
            ],
            "confidence": 1.0,
            "evidence": "rook on the open d-file"
          },
          {
            "theme": "bishop_pair",
            "squares": [
              "b5",
              "g5"
            ],
            "pieces": [
              "B@b5",
              "B@g5"
            ],
            "confidence": 1.0,
            "evidence": "the mover owns both bishops"
          },
          {
            "theme": "controls_center",
            "squares": [],
            "pieces": [],
            "confidence": 0.8,
            "evidence": "central control rises from 1.00 to 2.00"
          }
        ],
        "positional_delta": {
          "material": 0.0,
          "mobility": 36.0,
          "king_safety": 0.0,
          "pawn_structure": 0.0,
          "space": 4.0,
          "activity": 5.0
        },
        "intent": [
          {
            "tag": "attacks_king",
            "evidence": "pressure on the enemy king rises",
            "moves": [],
            "confidence": 0.7
          }
        ],
        "pv": [
          "h1d1",
          "e7c5",
          "g5f6",
          "f8d6",
          "b5d7",
          "e8d7",
          "b3f7",
          "d7c6",
          "f6g7",
          "h8b8",
          "a2a4",
          "b8b4"
        ],
        "fen_after": "4kb1r/p2rqppp/5n2/1B2p1B1/4P3/1Q6/PPP2PPP/2KR4 b k - 1 14",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 35969,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 27,
        "fen_before": "4kb1r/p2rqppp/5n2/1B2p1B1/4P3/1Q6/PPP2PPP/2KR4 b k - 1 14",
        "move_uci": "e7e6",
        "move_san": "Qe6",
        "quality": {
          "label": "excellent",
          "eval_before_cp": -716.0,
          "eval_after_cp": -811.0,
          "win_prob_before": 0.06683411803730019,
          "win_prob_after": 0.048054734297585326,
          "loss_cp": 95.0,
          "loss_wp": 0.018779383739714862,
          "best_move": "e7c5",
          "best_move_san": "Qc5",
          "best_move_cp": -716.0,
          "best_move_wp": 0.06683411803730019,
          "rank": 2,
          "n_lines": 3,
          "played_in_multipv": true,
          "is_only_move": false,
          "gap_to_second_wp": 0.018779383739714862,
          "sharpness": 0.02108333657596429,
          "is_forcing": false,
          "is_critical": false
        },
        "themes": [
          {
            "theme": "skewer",
            "squares": [
              "e6",
              "b3",
              "a2"
            ],
            "pieces": [
              "q@e6"
            ],
            "confidence": 0.7,
            "evidence": "q@e6 skewers the valuable Q@b3, which must step aside and let P@a2 fall"
          },
          {
            "theme": "threat_created",
            "squares": [
              "b3"
            ],
            "pieces": [
              "Q@b3",
              "q@e6"
            ],
            "confidence": 0.8,
            "evidence": "the move now attacks the defended Q@b3"
          },
          {
            "theme": "interference",
            "squares": [
              "b3",
              "e6",
              "f7"
            ],
            "pieces": [
              "Q@b3",
              "q@e6"
            ],
            "confidence": 0.7,
            "evidence": "q@e6 interposes on the Q@b3's line, denying the capture on f7"
          },
          {
            "theme": "shelters_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 1.0,
            "evidence": "king safety rises from -4.00 to -3.00"
          },
          {
            "theme": "weakens_opponent_king",
            "squares": [
              "c1"
            ],
            "pieces": [
              "K@c1"
            ],
            "confidence": 0.7,
            "evidence": "opponent king safety drops from -1.00 to -2.00"
          },
          {
            "theme": "isolated_pawn",
            "squares": [
              "a7"
            ],
            "pieces": [
              "p@a7"
            ],
            "confidence": 1.0,
            "evidence": "isolated pawn on a7"
          }
        ],
        "positional_delta": {
          "material": 0.0,
          "mobility": 66.0,
          "king_safety": 12.0,
          "pawn_structure": 0.0,
          "space": 0.0,
          "activity": -2.5
        },
        "intent": [
          {
            "tag": "improves_piece",
            "evidence": "the q moves toward the centre",
            "moves": [],
            "confidence": 0.7
          },
          {
            "tag": "restricts_opponent",
            "evidence": "opponent mobility drops from 37.0 to 36.0",
            "moves": [],
            "confidence": 0.7
          },
          {
            "tag": "attacks_king",
            "evidence": "pressure on the enemy king rises",
            "moves": [],
            "confidence": 0.7
          }
        ],
        "pv": [
          "e7e6",
          "g5f6",
          "g7f6",
          "b5d7",
          "e6d7",
          "b3b8",
          "e8e7",
          "d1d7",
          "e7d7",
          "b8b7",
          "d7e6"
        ],
        "fen_after": "4kb1r/p2r1ppp/4qn2/1B2p1B1/4P3/1Q6/PPP2PPP/2KR4 w k - 2 15",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 20506,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 28,
        "fen_before": "4kb1r/p2r1ppp/4qn2/1B2p1B1/4P3/1Q6/PPP2PPP/2KR4 w k - 2 15",
        "move_uci": "b5d7",
        "move_san": "Bxd7+",
        "quality": {
          "label": "best",
          "eval_before_cp": 999.0,
          "eval_after_cp": 999.0,
          "win_prob_before": 0.9753590969498981,
          "win_prob_after": 0.9753590969498981,
          "loss_cp": 0.0,
          "loss_wp": 0.0,
          "best_move": "b5d7",
          "best_move_san": "Bxd7+",
          "best_move_cp": 999.0,
          "best_move_wp": 0.9753590969498981,
          "rank": 1,
          "n_lines": 3,
          "played_in_multipv": true,
          "is_only_move": false,
          "gap_to_second_wp": 0.02192038849378042,
          "sharpness": 0.08279575845638354,
          "is_forcing": true,
          "is_critical": false
        },
        "themes": [
          {
            "theme": "fork",
            "squares": [
              "d7",
              "e6",
              "e8"
            ],
            "pieces": [
              "B@d7"
            ],
            "confidence": 1.0,
            "evidence": "B@d7 hits q@e6 and k@e8 at once and does not hang"
          },
          {
            "theme": "skewer",
            "squares": [
              "b3",
              "e6",
              "f7"
            ],
            "pieces": [
              "Q@b3"
            ],
            "confidence": 0.7,
            "evidence": "Q@b3 skewers the valuable q@e6, which must step aside and let p@f7 fall"
          },
          {
            "theme": "hanging_piece",
            "squares": [
              "e6"
            ],
            "pieces": [
              "q@e6"
            ],
            "confidence": 1.0,
            "evidence": "q@e6 is left hanging (1 attackers against its defenders)"
          },
          {
            "theme": "trapped_piece",
            "squares": [
              "e6"
            ],
            "pieces": [
              "q@e6"
            ],
            "confidence": 0.7,
            "evidence": "q@e6 is attacked and every square it can reach is covered too"
          },
          {
            "theme": "capture",
            "squares": [
              "b5",
              "d7"
            ],
            "pieces": [
              "B@d7"
            ],
            "confidence": 1.0,
            "evidence": "takes the r@d7"
          },
          {
            "theme": "shelters_king",
            "squares": [
              "c1"
            ],
            "pieces": [
              "K@c1"
            ],
            "confidence": 1.0,
            "evidence": "king safety rises from -2.00 to 1.00"
          },
          {
            "theme": "weakens_opponent_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 0.7,
            "evidence": "opponent king safety drops from -3.00 to -4.00"
          },
          {
            "theme": "passed_pawn",
            "squares": [
              "c2"
            ],
            "pieces": [
              "P@c2"
            ],
            "confidence": 1.0,
            "evidence": "passed pawn on c2"
          },
          {
            "theme": "bishop_pair",
            "squares": [
              "g5",
              "d7"
            ],
            "pieces": [
              "B@g5",
              "B@d7"
            ],
            "confidence": 1.0,
            "evidence": "the mover owns both bishops"
          }
        ],
        "positional_delta": {
          "material": 500.0,
          "mobility": 6.0,
          "king_safety": 36.0,
          "pawn_structure": 0.0,
          "space": 0.0,
          "activity": 5.0
        },
        "intent": [
          {
            "tag": "restricts_opponent",
            "evidence": "opponent mobility drops from 32.0 to 24.0",
            "moves": [],
            "confidence": 0.7
          },
          {
            "tag": "attacks_king",
            "evidence": "Bxd7+ gives check",
            "moves": [],
            "confidence": 1.0
          }
        ],
        "pv": [
          "b5d7",
          "e6d7",
          "b3b8",
          "e8e7",
          "d1d7",
          "e7d7",
          "b8b7",
          "d7e6",
          "b7a6",
          "f8d6"
        ],
        "fen_after": "4kb1r/p2B1ppp/4qn2/4p1B1/4P3/1Q6/PPP2PPP/2KR4 b k - 0 15",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 19100,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 29,
        "fen_before": "4kb1r/p2B1ppp/4qn2/4p1B1/4P3/1Q6/PPP2PPP/2KR4 b k - 0 15",
        "move_uci": "f6d7",
        "move_san": "Nxd7",
        "quality": {
          "label": "great",
          "eval_before_cp": -315.0,
          "eval_after_cp": -315.0,
          "win_prob_before": 0.23869359706743173,
          "win_prob_after": 0.23869359706743173,
          "loss_cp": 0.0,
          "loss_wp": 0.0,
          "best_move": "f6d7",
          "best_move_san": "Nxd7",
          "best_move_cp": -315.0,
          "best_move_wp": 0.23869359706743173,
          "rank": 1,
          "n_lines": 3,
          "played_in_multipv": true,
          "is_only_move": true,
          "gap_to_second_wp": 0.21333473988921142,
          "sharpness": 0.2347161114623224,
          "is_forcing": true,
          "is_critical": true
        },
        "themes": [
          {
            "theme": "skewer",
            "squares": [
              "e6",
              "b3",
              "a2"
            ],
            "pieces": [
              "q@e6"
            ],
            "confidence": 0.7,
            "evidence": "q@e6 skewers the valuable Q@b3, which must step aside and let P@a2 fall"
          },
          {
            "theme": "hanging_piece_defended",
            "squares": [
              "e6",
              "d7"
            ],
            "pieces": [
              "q@e6",
              "n@d7"
            ],
            "confidence": 1.0,
            "evidence": "q@e6 was hanging and is now covered by n@d7"
          },
          {
            "theme": "capture",
            "squares": [
              "f6",
              "d7"
            ],
            "pieces": [
              "n@d7"
            ],
            "confidence": 1.0,
            "evidence": "takes the B@d7"
          },
          {
            "theme": "exposes_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 1.0,
            "evidence": "king safety drops from -4.00 to -5.00"
          },
          {
            "theme": "isolated_pawn",
            "squares": [
              "a7"
            ],
            "pieces": [
              "p@a7"
            ],
            "confidence": 1.0,
            "evidence": "isolated pawn on a7"
          }
        ],
        "positional_delta": {
          "material": 330.0,
          "mobility": 0.0,
          "king_safety": -12.0,
          "pawn_structure": 0.0,
          "space": -4.0,
          "activity": -5.0
        },
        "intent": [
          {
            "tag": "restricts_opponent",
            "evidence": "opponent mobility drops from 37.0 to 34.0",
            "moves": [],
            "confidence": 0.7
          },
          {
            "tag": "defends_material",
            "evidence": "the move covers an attacked piece",
            "moves": [],
            "confidence": 1.0
          }
        ],
        "pv": [
          "f6d7",
          "b3b7",
          "f7f6",
          "b7c8",
          "e8e7",
          "g5e3",
          "a7a6",
          "a2a4",
          "h7h5",
          "a4a5",
          "g7g5",
          "c1b1",
          "h5h4",
          "c8c7"
        ],
        "fen_after": "4kb1r/p2n1ppp/4q3/4p1B1/4P3/1Q6/PPP2PPP/2KR4 w k - 0 16",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 12522,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 30,
        "fen_before": "4kb1r/p2n1ppp/4q3/4p1B1/4P3/1Q6/PPP2PPP/2KR4 w k - 0 16",
        "move_uci": "b3b8",
        "move_san": "Qb8+",
        "quality": {
          "label": "great",
          "eval_before_cp": 9998.0,
          "eval_after_cp": 9998.0,
          "win_prob_before": 1.0,
          "win_prob_after": 1.0,
          "loss_cp": 0.0,
          "loss_wp": 0.0,
          "best_move": "b3b8",
          "best_move_san": "Qb8+",
          "best_move_cp": 9998.0,
          "best_move_wp": 1.0,
          "rank": 1,
          "n_lines": 3,
          "played_in_multipv": true,
          "is_only_move": true,
          "gap_to_second_wp": 0.21234958051732766,
          "sharpness": 0.2340414606810215,
          "is_forcing": true,
          "is_critical": true
        },
        "themes": [
          {
            "theme": "x_ray",
            "squares": [
              "b8",
              "e8",
              "f8"
            ],
            "pieces": [
              "Q@b8"
            ],
            "confidence": 0.6,
            "evidence": "Q@b8 sees through k@e8 to the valuable b@f8 behind it"
          },
          {
            "theme": "passed_pawn",
            "squares": [
              "c2"
            ],
            "pieces": [
              "P@c2"
            ],
            "confidence": 1.0,
            "evidence": "passed pawn on c2"
          },
          {
            "theme": "controls_center",
            "squares": [],
            "pieces": [],
            "confidence": 0.8,
            "evidence": "central control rises from 2.00 to 3.00"
          }
        ],
        "positional_delta": {
          "material": 0.0,
          "mobility": -18.0,
          "king_safety": 0.0,
          "pawn_structure": 0.0,
          "space": 4.0,
          "activity": 2.5
        },
        "intent": [
          {
            "tag": "attacks_king",
            "evidence": "Qb8+ gives check",
            "moves": [],
            "confidence": 1.0
          }
        ],
        "pv": [
          "b3b8",
          "d7b8",
          "d1d8"
        ],
        "fen_after": "1Q2kb1r/p2n1ppp/4q3/4p1B1/4P3/8/PPP2PPP/2KR4 b k - 1 16",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 7238,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 31,
        "fen_before": "1Q2kb1r/p2n1ppp/4q3/4p1B1/4P3/8/PPP2PPP/2KR4 b k - 1 16",
        "move_uci": "d7b8",
        "move_san": "Nxb8",
        "quality": {
          "label": "best",
          "eval_before_cp": -9999.0,
          "eval_after_cp": -9999.0,
          "win_prob_before": 0.0,
          "win_prob_after": 0.0,
          "loss_cp": 0.0,
          "loss_wp": 0.0,
          "best_move": "d7b8",
          "best_move_san": "Nxb8",
          "best_move_cp": -9999.0,
          "best_move_wp": 0.0,
          "rank": 1,
          "n_lines": 1,
          "played_in_multipv": true,
          "is_only_move": false,
          "gap_to_second_wp": 0.0,
          "sharpness": 0.0,
          "is_forcing": true,
          "is_critical": false
        },
        "themes": [
          {
            "theme": "capture",
            "squares": [
              "d7",
              "b8"
            ],
            "pieces": [
              "n@b8"
            ],
            "confidence": 1.0,
            "evidence": "takes the Q@b8"
          },
          {
            "theme": "shelters_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 1.0,
            "evidence": "king safety rises from -5.00 to -4.00"
          },
          {
            "theme": "isolated_pawn",
            "squares": [
              "a7"
            ],
            "pieces": [
              "p@a7"
            ],
            "confidence": 1.0,
            "evidence": "isolated pawn on a7"
          }
        ],
        "positional_delta": {
          "material": 900.0,
          "mobility": 6.0,
          "king_safety": 12.0,
          "pawn_structure": 0.0,
          "space": 0.0,
          "activity": -5.0
        },
        "intent": [
          {
            "tag": "restricts_opponent",
            "evidence": "opponent mobility drops from 31.0 to 19.0",
            "moves": [],
            "confidence": 0.7
          }
        ],
        "pv": [
          "d7b8",
          "d1d8"
        ],
        "fen_after": "1n2kb1r/p4ppp/4q3/4p1B1/4P3/8/PPP2PPP/2KR4 w k - 0 17",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 24,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      },
      {
        "ply": 32,
        "fen_before": "1n2kb1r/p4ppp/4q3/4p1B1/4P3/8/PPP2PPP/2KR4 w k - 0 17",
        "move_uci": "d1d8",
        "move_san": "Rd8#",
        "quality": {
          "label": "great",
          "eval_before_cp": 9999.0,
          "eval_after_cp": 9999.0,
          "win_prob_before": 1.0,
          "win_prob_after": 1.0,
          "loss_cp": 0.0,
          "loss_wp": 0.0,
          "best_move": "d1d8",
          "best_move_san": "Rd8#",
          "best_move_cp": 9999.0,
          "best_move_wp": 1.0,
          "rank": 1,
          "n_lines": 3,
          "played_in_multipv": true,
          "is_only_move": true,
          "gap_to_second_wp": 0.9556743931791771,
          "sharpness": 0.9566008847009226,
          "is_forcing": true,
          "is_critical": true
        },
        "themes": [
          {
            "theme": "fork",
            "squares": [
              "d8",
              "b8",
              "e8"
            ],
            "pieces": [
              "R@d8"
            ],
            "confidence": 1.0,
            "evidence": "R@d8 hits n@b8 and k@e8 at once and does not hang"
          },
          {
            "theme": "hanging_piece",
            "squares": [
              "b8"
            ],
            "pieces": [
              "n@b8"
            ],
            "confidence": 1.0,
            "evidence": "n@b8 is left hanging (1 attackers against its defenders)"
          },
          {
            "theme": "back_rank_mate",
            "squares": [
              "d8",
              "e8"
            ],
            "pieces": [
              "R@d8"
            ],
            "confidence": 1.0,
            "evidence": "Rd8# mates: the king on e8 never left its back rank"
          },
          {
            "theme": "x_ray",
            "squares": [
              "d8",
              "e8",
              "f8"
            ],
            "pieces": [
              "R@d8"
            ],
            "confidence": 0.6,
            "evidence": "R@d8 sees through k@e8 to the valuable b@f8 behind it"
          },
          {
            "theme": "weakens_opponent_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 0.7,
            "evidence": "opponent king safety drops from -4.00 to -5.00"
          },
          {
            "theme": "passed_pawn",
            "squares": [
              "c2"
            ],
            "pieces": [
              "P@c2"
            ],
            "confidence": 1.0,
            "evidence": "passed pawn on c2"
          },
          {
            "theme": "rook_open_file",
            "squares": [
              "d8"
            ],
            "pieces": [
              "R@d8"
            ],
            "confidence": 1.0,
            "evidence": "rook on the open d-file"
          },
          {
            "theme": "develops_piece",
            "squares": [
              "d1",
              "d8"
            ],
            "pieces": [
              "R@d8"
            ],
            "confidence": 1.0,
            "evidence": "R@d8 develops off the back rank"
          }
        ],
        "positional_delta": {
          "material": 0.0,
          "mobility": -12.0,
          "king_safety": 0.0,
          "pawn_structure": 0.0,
          "space": 0.0,
          "activity": 0.0
        },
        "intent": [
          {
            "tag": "develops",
            "evidence": "develops the R to d8",
            "moves": [],
            "confidence": 1.0
          },
          {
            "tag": "attacks_king",
            "evidence": "Rd8# gives check",
            "moves": [],
            "confidence": 1.0
          }
        ],
        "pv": [
          "d1d8"
        ],
        "fen_after": "1n1Rkb1r/p4ppp/4q3/4p1B1/4P3/8/PPP2PPP/2K5 b k - 1 17",
        "meta": {
          "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
          "engine_id": "Stockfish 19",
          "limit_signature": "d12",
          "depth": 12,
          "nodes": 45608,
          "multipv": 3,
          "tier": 1,
          "source": "engine",
          "label_source": "engine",
          "puzzle_tags": [],
          "cache_hit": true,
          "dataset_version": "v1"
        },
        "provenance": {
          "engine_name": "Stockfish 19",
          "engine_author": "the Stockfish developers (see AUTHORS file)",
          "limit_type": "depth",
          "limit_value": 12.0,
          "multipv": 3,
          "threads": 1,
          "hash_mb": 256,
          "moveexp_version": "0.1.0"
        }
      }
    ],
    "meta": {
      "engine_path": "C:\\Users\\Walnut Icecream\\Documents\\chess-cnn\\tools\\stockfish\\stockfish\\stockfish-windows-x86-64-universal.exe",
      "engine_id": null,
      "limit_signature": "d12",
      "depth": 0,
      "nodes": 0,
      "multipv": 3,
      "tier": 1,
      "source": "engine",
      "label_source": "engine",
      "puzzle_tags": [],
      "cache_hit": false,
      "dataset_version": "v1"
    },
    "provenance": {
      "engine_name": "Stockfish 19",
      "engine_author": "the Stockfish developers (see AUTHORS file)",
      "limit_type": "depth",
      "limit_value": 12.0,
      "multipv": 3,
      "threads": 1,
      "hash_mb": 256,
      "moveexp_version": "0.1.0"
    }
  },
  "explanations": [
    {
      "ply": 0,
      "move_san": "e4",
      "move_uci": "e2e4",
      "headline": "e4 \u2014 the best move.",
      "sentences": [
        "The evaluation remains +0.30 for the mover.",
        "Exposes king: king safety drops from 3.00 to 2.00.",
        "Bishop pair: the mover owns both bishops.",
        "Bad bishop: bishop on c1 is blocked by its own pawns.",
        "Controls center: central control rises from 0.00 to 1.00.",
        "Mobility: improved by 60.0.",
        "King safety: worsened by 12.0.",
        "Space: improved by 4.0."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "e4 \u2014 the best move.",
          "evidence": "quality.label=best",
          "source": {
            "move_san": "e4",
            "label": "best"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "The evaluation remains +0.30 for the mover.",
          "evidence": "eval_before_cp=30.0, eval_after_cp=30.0, loss_cp=0.0, loss_wp=0.000",
          "source": {
            "label": "best",
            "eval_after_cp": 30.0,
            "loss_cp": 0.0,
            "loss_wp": 0.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Exposes king: king safety drops from 3.00 to 2.00.",
          "evidence": "king safety drops from 3.00 to 2.00",
          "source": {
            "theme": "exposes_king",
            "squares": [
              "e1"
            ],
            "pieces": [
              "K@e1"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bishop pair: the mover owns both bishops.",
          "evidence": "the mover owns both bishops",
          "source": {
            "theme": "bishop_pair",
            "squares": [
              "c1",
              "f1"
            ],
            "pieces": [
              "B@c1",
              "B@f1"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bad bishop: bishop on c1 is blocked by its own pawns.",
          "evidence": "bishop on c1 is blocked by its own pawns",
          "source": {
            "theme": "bad_bishop",
            "squares": [
              "c1"
            ],
            "pieces": [
              "B@c1"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Controls center: central control rises from 0.00 to 1.00.",
          "evidence": "central control rises from 0.00 to 1.00",
          "source": {
            "theme": "controls_center",
            "squares": [],
            "pieces": [],
            "confidence": 0.8
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Mobility: improved by 60.0.",
          "evidence": "positional_delta.mobility=60.0",
          "source": {
            "group": "mobility",
            "value": 60.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "King safety: worsened by 12.0.",
          "evidence": "positional_delta.king_safety=-12.0",
          "source": {
            "group": "king_safety",
            "value": -12.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Space: improved by 4.0.",
          "evidence": "positional_delta.space=4.0",
          "source": {
            "group": "space",
            "value": 4.0
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 1,
      "move_san": "e5",
      "move_uci": "e7e5",
      "headline": "e5 \u2014 an excellent move.",
      "sentences": [
        "The evaluation remains -0.41 for the mover.",
        "Exposes king: king safety drops from 3.00 to 2.00.",
        "Bishop pair: the mover owns both bishops.",
        "Bad bishop: bishop on c8 is blocked by its own pawns.",
        "Controls center: central control rises from 0.00 to 1.00.",
        "Mobility: improved by 60.0.",
        "King safety: worsened by 12.0.",
        "Space: improved by 4.0."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "e5 \u2014 an excellent move.",
          "evidence": "quality.label=excellent",
          "source": {
            "move_san": "e5",
            "label": "excellent"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "The evaluation remains -0.41 for the mover.",
          "evidence": "eval_before_cp=-32.0, eval_after_cp=-41.0, loss_cp=9.0, loss_wp=0.008",
          "source": {
            "label": "excellent",
            "eval_after_cp": -41.0,
            "loss_cp": 9.0,
            "loss_wp": 0.008247196177410876
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Exposes king: king safety drops from 3.00 to 2.00.",
          "evidence": "king safety drops from 3.00 to 2.00",
          "source": {
            "theme": "exposes_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bishop pair: the mover owns both bishops.",
          "evidence": "the mover owns both bishops",
          "source": {
            "theme": "bishop_pair",
            "squares": [
              "c8",
              "f8"
            ],
            "pieces": [
              "b@c8",
              "b@f8"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bad bishop: bishop on c8 is blocked by its own pawns.",
          "evidence": "bishop on c8 is blocked by its own pawns",
          "source": {
            "theme": "bad_bishop",
            "squares": [
              "c8"
            ],
            "pieces": [
              "b@c8"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Controls center: central control rises from 0.00 to 1.00.",
          "evidence": "central control rises from 0.00 to 1.00",
          "source": {
            "theme": "controls_center",
            "squares": [],
            "pieces": [],
            "confidence": 0.8
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Mobility: improved by 60.0.",
          "evidence": "positional_delta.mobility=60.0",
          "source": {
            "group": "mobility",
            "value": 60.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "King safety: worsened by 12.0.",
          "evidence": "positional_delta.king_safety=-12.0",
          "source": {
            "group": "king_safety",
            "value": -12.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Space: improved by 4.0.",
          "evidence": "positional_delta.space=4.0",
          "source": {
            "group": "space",
            "value": 4.0
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 2,
      "move_san": "Nf3",
      "move_uci": "g1f3",
      "headline": "Nf3 \u2014 the best move.",
      "sentences": [
        "The evaluation remains +0.27 for the mover.",
        "Bishop pair: the mover owns both bishops.",
        "Bad bishop: bishop on c1 is blocked by its own pawns.",
        "Develops piece: N@f3 develops off the back rank.",
        "Controls center: central control rises from 1.00 to 3.00.",
        "Space: improved by 8.0.",
        "Activity: improved by 10.0.",
        "Intent \u2014 improves piece: the N moves toward the centre.",
        "Intent \u2014 develops: develops the N to f3."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "Nf3 \u2014 the best move.",
          "evidence": "quality.label=best",
          "source": {
            "move_san": "Nf3",
            "label": "best"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "The evaluation remains +0.27 for the mover.",
          "evidence": "eval_before_cp=27.0, eval_after_cp=27.0, loss_cp=0.0, loss_wp=0.000",
          "source": {
            "label": "best",
            "eval_after_cp": 27.0,
            "loss_cp": 0.0,
            "loss_wp": 0.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bishop pair: the mover owns both bishops.",
          "evidence": "the mover owns both bishops",
          "source": {
            "theme": "bishop_pair",
            "squares": [
              "c1",
              "f1"
            ],
            "pieces": [
              "B@c1",
              "B@f1"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bad bishop: bishop on c1 is blocked by its own pawns.",
          "evidence": "bishop on c1 is blocked by its own pawns",
          "source": {
            "theme": "bad_bishop",
            "squares": [
              "c1"
            ],
            "pieces": [
              "B@c1"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Develops piece: N@f3 develops off the back rank.",
          "evidence": "N@f3 develops off the back rank",
          "source": {
            "theme": "develops_piece",
            "squares": [
              "g1",
              "f3"
            ],
            "pieces": [
              "N@f3"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Controls center: central control rises from 1.00 to 3.00.",
          "evidence": "central control rises from 1.00 to 3.00",
          "source": {
            "theme": "controls_center",
            "squares": [],
            "pieces": [],
            "confidence": 0.8
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Space: improved by 8.0.",
          "evidence": "positional_delta.space=8.0",
          "source": {
            "group": "space",
            "value": 8.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Activity: improved by 10.0.",
          "evidence": "positional_delta.activity=10.0",
          "source": {
            "group": "activity",
            "value": 10.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 improves piece: the N moves toward the centre.",
          "evidence": "the N moves toward the centre",
          "source": {
            "tag": "improves_piece",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 develops: develops the N to f3.",
          "evidence": "develops the N to f3",
          "source": {
            "tag": "develops",
            "moves": [],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 3,
      "move_san": "d6",
      "move_uci": "d7d6",
      "headline": "d6 \u2014 a good move.",
      "sentences": [
        "It gives up 0.41 pawns (4% win probability).",
        "Bishop pair: the mover owns both bishops.",
        "Controls center: central control rises from 1.00 to 2.00.",
        "Mobility: improved by 18.0.",
        "Space: improved by 4.0.",
        "The engine preferred Nf6."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "d6 \u2014 a good move.",
          "evidence": "quality.label=good",
          "source": {
            "move_san": "d6",
            "label": "good"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "It gives up 0.41 pawns (4% win probability).",
          "evidence": "eval_before_cp=-27.0, eval_after_cp=-68.0, loss_cp=41.0, loss_wp=0.037",
          "source": {
            "label": "good",
            "eval_after_cp": -68.0,
            "loss_cp": 41.0,
            "loss_wp": 0.03743679439019665
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bishop pair: the mover owns both bishops.",
          "evidence": "the mover owns both bishops",
          "source": {
            "theme": "bishop_pair",
            "squares": [
              "c8",
              "f8"
            ],
            "pieces": [
              "b@c8",
              "b@f8"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Controls center: central control rises from 1.00 to 2.00.",
          "evidence": "central control rises from 1.00 to 2.00",
          "source": {
            "theme": "controls_center",
            "squares": [],
            "pieces": [],
            "confidence": 0.8
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Mobility: improved by 18.0.",
          "evidence": "positional_delta.mobility=18.0",
          "source": {
            "group": "mobility",
            "value": 18.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Space: improved by 4.0.",
          "evidence": "positional_delta.space=4.0",
          "source": {
            "group": "space",
            "value": 4.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "engine",
          "text": "The engine preferred Nf6.",
          "evidence": "best_move=g8f6, label=good",
          "source": {
            "best_move": "g8f6",
            "label": "good"
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 4,
      "move_san": "d4",
      "move_uci": "d2d4",
      "headline": "d4 \u2014 the best move.",
      "sentences": [
        "The evaluation remains +0.68 for the mover.",
        "Exposes king: king safety drops from 2.00 to 1.00.",
        "Pawn break: pawn on d4 attacks an enemy pawn.",
        "Bishop pair: the mover owns both bishops.",
        "Mobility: improved by 48.0.",
        "King safety: worsened by 12.0."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "d4 \u2014 the best move.",
          "evidence": "quality.label=best",
          "source": {
            "move_san": "d4",
            "label": "best"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "The evaluation remains +0.68 for the mover.",
          "evidence": "eval_before_cp=68.0, eval_after_cp=68.0, loss_cp=0.0, loss_wp=0.000",
          "source": {
            "label": "best",
            "eval_after_cp": 68.0,
            "loss_cp": 0.0,
            "loss_wp": 0.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Exposes king: king safety drops from 2.00 to 1.00.",
          "evidence": "king safety drops from 2.00 to 1.00",
          "source": {
            "theme": "exposes_king",
            "squares": [
              "e1"
            ],
            "pieces": [
              "K@e1"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Pawn break: pawn on d4 attacks an enemy pawn.",
          "evidence": "pawn on d4 attacks an enemy pawn",
          "source": {
            "theme": "pawn_break",
            "squares": [
              "d4"
            ],
            "pieces": [
              "P@d4"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bishop pair: the mover owns both bishops.",
          "evidence": "the mover owns both bishops",
          "source": {
            "theme": "bishop_pair",
            "squares": [
              "c1",
              "f1"
            ],
            "pieces": [
              "B@c1",
              "B@f1"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Mobility: improved by 48.0.",
          "evidence": "positional_delta.mobility=48.0",
          "source": {
            "group": "mobility",
            "value": 48.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "King safety: worsened by 12.0.",
          "evidence": "positional_delta.king_safety=-12.0",
          "source": {
            "group": "king_safety",
            "value": -12.0
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 5,
      "move_san": "Bg4",
      "move_uci": "c8g4",
      "headline": "Bg4 \u2014 a good move.",
      "sentences": [
        "It gives up 0.23 pawns (2% win probability).",
        "Threat created: the move now attacks the defended N@f3.",
        "X ray: b@g4 sees through N@f3 to the valuable Q@d1 behind it.",
        "Weakens opponent king: opponent king safety drops from 1.00 to 0.00.",
        "Bishop pair: the mover owns both bishops.",
        "Develops piece: b@g4 develops off the back rank.",
        "Mobility: improved by 18.0.",
        "Activity: improved by 5.0.",
        "Intent \u2014 improves piece: the b moves toward the centre.",
        "Intent \u2014 develops: develops the b to g4.",
        "Intent \u2014 attacks king: pressure on the enemy king rises.",
        "The engine preferred Nd7."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "Bg4 \u2014 a good move.",
          "evidence": "quality.label=good",
          "source": {
            "move_san": "Bg4",
            "label": "good"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "It gives up 0.23 pawns (2% win probability).",
          "evidence": "eval_before_cp=-55.0, eval_after_cp=-78.0, loss_cp=23.0, loss_wp=0.021",
          "source": {
            "label": "good",
            "eval_after_cp": -78.0,
            "loss_cp": 23.0,
            "loss_wp": 0.02085478273290603
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Threat created: the move now attacks the defended N@f3.",
          "evidence": "the move now attacks the defended N@f3",
          "source": {
            "theme": "threat_created",
            "squares": [
              "f3"
            ],
            "pieces": [
              "N@f3",
              "b@g4"
            ],
            "confidence": 0.8
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "X ray: b@g4 sees through N@f3 to the valuable Q@d1 behind it.",
          "evidence": "b@g4 sees through N@f3 to the valuable Q@d1 behind it",
          "source": {
            "theme": "x_ray",
            "squares": [
              "g4",
              "f3",
              "d1"
            ],
            "pieces": [
              "b@g4"
            ],
            "confidence": 0.6
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Weakens opponent king: opponent king safety drops from 1.00 to 0.00.",
          "evidence": "opponent king safety drops from 1.00 to 0.00",
          "source": {
            "theme": "weakens_opponent_king",
            "squares": [
              "e1"
            ],
            "pieces": [
              "K@e1"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bishop pair: the mover owns both bishops.",
          "evidence": "the mover owns both bishops",
          "source": {
            "theme": "bishop_pair",
            "squares": [
              "g4",
              "f8"
            ],
            "pieces": [
              "b@g4",
              "b@f8"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Develops piece: b@g4 develops off the back rank.",
          "evidence": "b@g4 develops off the back rank",
          "source": {
            "theme": "develops_piece",
            "squares": [
              "c8",
              "g4"
            ],
            "pieces": [
              "b@g4"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Mobility: improved by 18.0.",
          "evidence": "positional_delta.mobility=18.0",
          "source": {
            "group": "mobility",
            "value": 18.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Activity: improved by 5.0.",
          "evidence": "positional_delta.activity=5.0",
          "source": {
            "group": "activity",
            "value": 5.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 improves piece: the b moves toward the centre.",
          "evidence": "the b moves toward the centre",
          "source": {
            "tag": "improves_piece",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 develops: develops the b to g4.",
          "evidence": "develops the b to g4",
          "source": {
            "tag": "develops",
            "moves": [],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 attacks king: pressure on the enemy king rises.",
          "evidence": "pressure on the enemy king rises",
          "source": {
            "tag": "attacks_king",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "engine",
          "text": "The engine preferred Nd7.",
          "evidence": "best_move=b8d7, label=good",
          "source": {
            "best_move": "b8d7",
            "label": "good"
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 6,
      "move_san": "dxe5",
      "move_uci": "d4e5",
      "headline": "dxe5 \u2014 an excellent move.",
      "sentences": [
        "The evaluation remains +0.82 for the mover.",
        "The move is forcing: a check or a forced mate.",
        "X ray: Q@d1 sees through p@d6 to the valuable q@d8 behind it.",
        "Capture: takes the p@e5.",
        "Weakens opponent king: opponent king safety drops from 2.00 to 0.00.",
        "Doubled pawn: doubled pawns on the e-file.",
        "Backward pawn: backward pawn on e5.",
        "Pawn island: pawn island count changes from 1 to 2.",
        "Pawn break: pawn on e5 attacks an enemy pawn.",
        "Bishop pair: the mover owns both bishops.",
        "Material: the mover gained 1.00 pawns.",
        "Mobility: improved by 18.0.",
        "Pawn structure: worsened by 40.0.",
        "Intent \u2014 attacks king: pressure on the enemy king rises."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "dxe5 \u2014 an excellent move.",
          "evidence": "quality.label=excellent",
          "source": {
            "move_san": "dxe5",
            "label": "excellent"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "The evaluation remains +0.82 for the mover.",
          "evidence": "eval_before_cp=95.0, eval_after_cp=82.0, loss_cp=13.0, loss_wp=0.012",
          "source": {
            "label": "excellent",
            "eval_after_cp": 82.0,
            "loss_cp": 13.0,
            "loss_wp": 0.011654106296593247
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "The move is forcing: a check or a forced mate.",
          "evidence": "is_forcing=True",
          "source": {
            "flag": "is_forcing",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "X ray: Q@d1 sees through p@d6 to the valuable q@d8 behind it.",
          "evidence": "Q@d1 sees through p@d6 to the valuable q@d8 behind it",
          "source": {
            "theme": "x_ray",
            "squares": [
              "d1",
              "d6",
              "d8"
            ],
            "pieces": [
              "Q@d1"
            ],
            "confidence": 0.6
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Capture: takes the p@e5.",
          "evidence": "takes the p@e5",
          "source": {
            "theme": "capture",
            "squares": [
              "d4",
              "e5"
            ],
            "pieces": [
              "P@e5"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Weakens opponent king: opponent king safety drops from 2.00 to 0.00.",
          "evidence": "opponent king safety drops from 2.00 to 0.00",
          "source": {
            "theme": "weakens_opponent_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Doubled pawn: doubled pawns on the e-file.",
          "evidence": "doubled pawns on the e-file",
          "source": {
            "theme": "doubled_pawn",
            "squares": [
              "e4"
            ],
            "pieces": [
              "P@e4"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Backward pawn: backward pawn on e5.",
          "evidence": "backward pawn on e5",
          "source": {
            "theme": "backward_pawn",
            "squares": [
              "e5"
            ],
            "pieces": [
              "P@e5"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Pawn island: pawn island count changes from 1 to 2.",
          "evidence": "pawn island count changes from 1 to 2",
          "source": {
            "theme": "pawn_island",
            "squares": [],
            "pieces": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Pawn break: pawn on e5 attacks an enemy pawn.",
          "evidence": "pawn on e5 attacks an enemy pawn",
          "source": {
            "theme": "pawn_break",
            "squares": [
              "e5"
            ],
            "pieces": [
              "P@e5"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bishop pair: the mover owns both bishops.",
          "evidence": "the mover owns both bishops",
          "source": {
            "theme": "bishop_pair",
            "squares": [
              "c1",
              "f1"
            ],
            "pieces": [
              "B@c1",
              "B@f1"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Material: the mover gained 1.00 pawns.",
          "evidence": "positional_delta.material=100.0",
          "source": {
            "group": "material",
            "value": 100.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Mobility: improved by 18.0.",
          "evidence": "positional_delta.mobility=18.0",
          "source": {
            "group": "mobility",
            "value": 18.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Pawn structure: worsened by 40.0.",
          "evidence": "positional_delta.pawn_structure=-40.0",
          "source": {
            "group": "pawn_structure",
            "value": -40.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 attacks king: pressure on the enemy king rises.",
          "evidence": "pressure on the enemy king rises",
          "source": {
            "tag": "attacks_king",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 7,
      "move_san": "Bxf3",
      "move_uci": "g4f3",
      "headline": "Bxf3 \u2014 an inaccuracy.",
      "sentences": [
        "It gives up 1.11 pawns (10% win probability).",
        "The move is forcing: a check or a forced mate.",
        "Pin: the cheap b@f3 holds the defended Q@d1 in place.",
        "Threat created: the move now attacks the defended Q@d1.",
        "X ray: b@f3 sees through P@g2 to the valuable R@h1 behind it.",
        "Capture: takes the N@f3.",
        "Trade: trades the b@g4 for the N@f3.",
        "Simplification: trades the b@g4 for the N@f3 and thins the board.",
        "Weakens opponent king: opponent king safety drops from 0.00 to -1.00.",
        "Backward pawn: backward pawn on d6.",
        "Bishop pair: the mover owns both bishops.",
        "Controls center: central control rises from 1.00 to 2.00.",
        "Material: the mover gained 3.20 pawns.",
        "Mobility: worsened by 6.0.",
        "Space: improved by 4.0.",
        "Activity: improved by 7.5.",
        "Intent \u2014 improves piece: the b moves toward the centre.",
        "Intent \u2014 restricts opponent: opponent mobility drops from 25.0 to 21.0.",
        "Intent \u2014 trades defender: the move removes the defender of e5.",
        "Intent \u2014 simplifies: an even exchange that thins the position.",
        "Intent \u2014 attacks king: pressure on the enemy king rises.",
        "The engine preferred Nd7."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "Bxf3 \u2014 an inaccuracy.",
          "evidence": "quality.label=inaccuracy",
          "source": {
            "move_san": "Bxf3",
            "label": "inaccuracy"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "It gives up 1.11 pawns (10% win probability).",
          "evidence": "eval_before_cp=-82.0, eval_after_cp=-193.0, loss_cp=111.0, loss_wp=0.096",
          "source": {
            "label": "inaccuracy",
            "eval_after_cp": -193.0,
            "loss_cp": 111.0,
            "loss_wp": 0.09562848881811126
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "The move is forcing: a check or a forced mate.",
          "evidence": "is_forcing=True",
          "source": {
            "flag": "is_forcing",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Pin: the cheap b@f3 holds the defended Q@d1 in place.",
          "evidence": "the cheap b@f3 holds the defended Q@d1 in place",
          "source": {
            "theme": "pin",
            "squares": [
              "d1"
            ],
            "pieces": [
              "Q@d1",
              "b@f3"
            ],
            "confidence": 0.6
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Threat created: the move now attacks the defended Q@d1.",
          "evidence": "the move now attacks the defended Q@d1",
          "source": {
            "theme": "threat_created",
            "squares": [
              "d1"
            ],
            "pieces": [
              "Q@d1",
              "b@f3"
            ],
            "confidence": 0.8
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "X ray: b@f3 sees through P@g2 to the valuable R@h1 behind it.",
          "evidence": "b@f3 sees through P@g2 to the valuable R@h1 behind it",
          "source": {
            "theme": "x_ray",
            "squares": [
              "f3",
              "g2",
              "h1"
            ],
            "pieces": [
              "b@f3"
            ],
            "confidence": 0.6
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Capture: takes the N@f3.",
          "evidence": "takes the N@f3",
          "source": {
            "theme": "capture",
            "squares": [
              "g4",
              "f3"
            ],
            "pieces": [
              "b@f3"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Trade: trades the b@g4 for the N@f3.",
          "evidence": "trades the b@g4 for the N@f3",
          "source": {
            "theme": "trade",
            "squares": [
              "g4",
              "f3"
            ],
            "pieces": [
              "b@f3"
            ],
            "confidence": 0.8
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Simplification: trades the b@g4 for the N@f3 and thins the board.",
          "evidence": "trades the b@g4 for the N@f3 and thins the board",
          "source": {
            "theme": "simplification",
            "squares": [
              "g4",
              "f3"
            ],
            "pieces": [
              "b@f3"
            ],
            "confidence": 0.8
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Weakens opponent king: opponent king safety drops from 0.00 to -1.00.",
          "evidence": "opponent king safety drops from 0.00 to -1.00",
          "source": {
            "theme": "weakens_opponent_king",
            "squares": [
              "e1"
            ],
            "pieces": [
              "K@e1"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Backward pawn: backward pawn on d6.",
          "evidence": "backward pawn on d6",
          "source": {
            "theme": "backward_pawn",
            "squares": [
              "d6"
            ],
            "pieces": [
              "p@d6"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bishop pair: the mover owns both bishops.",
          "evidence": "the mover owns both bishops",
          "source": {
            "theme": "bishop_pair",
            "squares": [
              "f3",
              "f8"
            ],
            "pieces": [
              "b@f3",
              "b@f8"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Controls center: central control rises from 1.00 to 2.00.",
          "evidence": "central control rises from 1.00 to 2.00",
          "source": {
            "theme": "controls_center",
            "squares": [],
            "pieces": [],
            "confidence": 0.8
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Material: the mover gained 3.20 pawns.",
          "evidence": "positional_delta.material=320.0",
          "source": {
            "group": "material",
            "value": 320.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Mobility: worsened by 6.0.",
          "evidence": "positional_delta.mobility=-6.0",
          "source": {
            "group": "mobility",
            "value": -6.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Space: improved by 4.0.",
          "evidence": "positional_delta.space=4.0",
          "source": {
            "group": "space",
            "value": 4.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Activity: improved by 7.5.",
          "evidence": "positional_delta.activity=7.5",
          "source": {
            "group": "activity",
            "value": 7.5
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 improves piece: the b moves toward the centre.",
          "evidence": "the b moves toward the centre",
          "source": {
            "tag": "improves_piece",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 restricts opponent: opponent mobility drops from 25.0 to 21.0.",
          "evidence": "opponent mobility drops from 25.0 to 21.0",
          "source": {
            "tag": "restricts_opponent",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 trades defender: the move removes the defender of e5.",
          "evidence": "the move removes the defender of e5",
          "source": {
            "tag": "trades_defender",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 simplifies: an even exchange that thins the position.",
          "evidence": "an even exchange that thins the position",
          "source": {
            "tag": "simplifies",
            "moves": [],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 attacks king: pressure on the enemy king rises.",
          "evidence": "pressure on the enemy king rises",
          "source": {
            "tag": "attacks_king",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "engine",
          "text": "The engine preferred Nd7.",
          "evidence": "best_move=b8d7, label=inaccuracy",
          "source": {
            "best_move": "b8d7",
            "label": "inaccuracy"
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 8,
      "move_san": "Qxf3",
      "move_uci": "d1f3",
      "headline": "Qxf3 \u2014 the best move.",
      "sentences": [
        "The evaluation remains +1.84 for the mover.",
        "The move is forcing: a check or a forced mate.",
        "The position was critical: small differences in the evaluation mattered.",
        "X ray: Q@f3 sees through p@f7 to the valuable b@f8 behind it.",
        "Capture: takes the b@f3.",
        "Shelters king: king safety rises from -1.00 to 1.00.",
        "Weakens opponent king: opponent king safety drops from 0.00 to -1.00.",
        "Doubled pawn: doubled pawns on the e-file.",
        "Backward pawn: backward pawn on e5.",
        "Bishop pair: the mover owns both bishops.",
        "Material: the mover gained 3.30 pawns.",
        "Mobility: improved by 48.0.",
        "King safety: improved by 24.0.",
        "Activity: worsened by 5.0.",
        "Intent \u2014 improves piece: the Q moves toward the centre.",
        "Intent \u2014 restricts opponent: opponent mobility drops from 19.0 to 13.0.",
        "Intent \u2014 attacks king: pressure on the enemy king rises."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "Qxf3 \u2014 the best move.",
          "evidence": "quality.label=best",
          "source": {
            "move_san": "Qxf3",
            "label": "best"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "The evaluation remains +1.84 for the mover.",
          "evidence": "eval_before_cp=184.0, eval_after_cp=184.0, loss_cp=0.0, loss_wp=0.000",
          "source": {
            "label": "best",
            "eval_after_cp": 184.0,
            "loss_cp": 0.0,
            "loss_wp": 0.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "The move is forcing: a check or a forced mate.",
          "evidence": "is_forcing=True",
          "source": {
            "flag": "is_forcing",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "The position was critical: small differences in the evaluation mattered.",
          "evidence": "is_critical=True, sharpness=0.458",
          "source": {
            "flag": "is_critical",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "X ray: Q@f3 sees through p@f7 to the valuable b@f8 behind it.",
          "evidence": "Q@f3 sees through p@f7 to the valuable b@f8 behind it",
          "source": {
            "theme": "x_ray",
            "squares": [
              "f3",
              "f7",
              "f8"
            ],
            "pieces": [
              "Q@f3"
            ],
            "confidence": 0.6
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Capture: takes the b@f3.",
          "evidence": "takes the b@f3",
          "source": {
            "theme": "capture",
            "squares": [
              "d1",
              "f3"
            ],
            "pieces": [
              "Q@f3"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Shelters king: king safety rises from -1.00 to 1.00.",
          "evidence": "king safety rises from -1.00 to 1.00",
          "source": {
            "theme": "shelters_king",
            "squares": [
              "e1"
            ],
            "pieces": [
              "K@e1"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Weakens opponent king: opponent king safety drops from 0.00 to -1.00.",
          "evidence": "opponent king safety drops from 0.00 to -1.00",
          "source": {
            "theme": "weakens_opponent_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Doubled pawn: doubled pawns on the e-file.",
          "evidence": "doubled pawns on the e-file",
          "source": {
            "theme": "doubled_pawn",
            "squares": [
              "e4"
            ],
            "pieces": [
              "P@e4"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Backward pawn: backward pawn on e5.",
          "evidence": "backward pawn on e5",
          "source": {
            "theme": "backward_pawn",
            "squares": [
              "e5"
            ],
            "pieces": [
              "P@e5"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bishop pair: the mover owns both bishops.",
          "evidence": "the mover owns both bishops",
          "source": {
            "theme": "bishop_pair",
            "squares": [
              "c1",
              "f1"
            ],
            "pieces": [
              "B@c1",
              "B@f1"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Material: the mover gained 3.30 pawns.",
          "evidence": "positional_delta.material=330.0",
          "source": {
            "group": "material",
            "value": 330.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Mobility: improved by 48.0.",
          "evidence": "positional_delta.mobility=48.0",
          "source": {
            "group": "mobility",
            "value": 48.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "King safety: improved by 24.0.",
          "evidence": "positional_delta.king_safety=24.0",
          "source": {
            "group": "king_safety",
            "value": 24.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Activity: worsened by 5.0.",
          "evidence": "positional_delta.activity=-5.0",
          "source": {
            "group": "activity",
            "value": -5.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 improves piece: the Q moves toward the centre.",
          "evidence": "the Q moves toward the centre",
          "source": {
            "tag": "improves_piece",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 restricts opponent: opponent mobility drops from 19.0 to 13.0.",
          "evidence": "opponent mobility drops from 19.0 to 13.0",
          "source": {
            "tag": "restricts_opponent",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 attacks king: pressure on the enemy king rises.",
          "evidence": "pressure on the enemy king rises",
          "source": {
            "tag": "attacks_king",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 9,
      "move_san": "dxe5",
      "move_uci": "d6e5",
      "headline": "dxe5 \u2014 the best move.",
      "sentences": [
        "The evaluation remains -1.88 for the mover.",
        "The move is forcing: a check or a forced mate.",
        "Capture: takes the P@e5.",
        "Weakens opponent king: opponent king safety drops from 1.00 to -2.00.",
        "Controls center: central control rises from 1.00 to 2.00.",
        "Material: the mover gained 1.00 pawns.",
        "Mobility: improved by 60.0.",
        "Pawn structure: improved by 20.0.",
        "Space: improved by 4.0.",
        "Intent \u2014 attacks king: pressure on the enemy king rises."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "dxe5 \u2014 the best move.",
          "evidence": "quality.label=best",
          "source": {
            "move_san": "dxe5",
            "label": "best"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "The evaluation remains -1.88 for the mover.",
          "evidence": "eval_before_cp=-188.0, eval_after_cp=-188.0, loss_cp=0.0, loss_wp=0.000",
          "source": {
            "label": "best",
            "eval_after_cp": -188.0,
            "loss_cp": 0.0,
            "loss_wp": 0.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "The move is forcing: a check or a forced mate.",
          "evidence": "is_forcing=True",
          "source": {
            "flag": "is_forcing",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Capture: takes the P@e5.",
          "evidence": "takes the P@e5",
          "source": {
            "theme": "capture",
            "squares": [
              "d6",
              "e5"
            ],
            "pieces": [
              "p@e5"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Weakens opponent king: opponent king safety drops from 1.00 to -2.00.",
          "evidence": "opponent king safety drops from 1.00 to -2.00",
          "source": {
            "theme": "weakens_opponent_king",
            "squares": [
              "e1"
            ],
            "pieces": [
              "K@e1"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Controls center: central control rises from 1.00 to 2.00.",
          "evidence": "central control rises from 1.00 to 2.00",
          "source": {
            "theme": "controls_center",
            "squares": [],
            "pieces": [],
            "confidence": 0.8
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Material: the mover gained 1.00 pawns.",
          "evidence": "positional_delta.material=100.0",
          "source": {
            "group": "material",
            "value": 100.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Mobility: improved by 60.0.",
          "evidence": "positional_delta.mobility=60.0",
          "source": {
            "group": "mobility",
            "value": 60.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Pawn structure: improved by 20.0.",
          "evidence": "positional_delta.pawn_structure=20.0",
          "source": {
            "group": "pawn_structure",
            "value": 20.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Space: improved by 4.0.",
          "evidence": "positional_delta.space=4.0",
          "source": {
            "group": "space",
            "value": 4.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 attacks king: pressure on the enemy king rises.",
          "evidence": "pressure on the enemy king rises",
          "source": {
            "tag": "attacks_king",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 10,
      "move_san": "Bc4",
      "move_uci": "f1c4",
      "headline": "Bc4 \u2014 a good move.",
      "sentences": [
        "It gives up 0.51 pawns (4% win probability).",
        "X ray: B@c4 sees through p@f7 to the valuable n@g8 behind it.",
        "Weakens opponent king: opponent king safety drops from -1.00 to -2.00.",
        "Bishop pair: the mover owns both bishops.",
        "Develops piece: B@c4 develops off the back rank.",
        "Mobility: improved by 30.0.",
        "Activity: improved by 7.5.",
        "Intent \u2014 improves piece: the B moves toward the centre.",
        "Intent \u2014 develops: develops the B to c4.",
        "Intent \u2014 attacks king: pressure on the enemy king rises.",
        "The engine preferred Qb3."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "Bc4 \u2014 a good move.",
          "evidence": "quality.label=good",
          "source": {
            "move_san": "Bc4",
            "label": "good"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "It gives up 0.51 pawns (4% win probability).",
          "evidence": "eval_before_cp=176.0, eval_after_cp=125.0, loss_cp=51.0, loss_wp=0.043",
          "source": {
            "label": "good",
            "eval_after_cp": 125.0,
            "loss_cp": 51.0,
            "loss_wp": 0.043494162730723596
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "X ray: B@c4 sees through p@f7 to the valuable n@g8 behind it.",
          "evidence": "B@c4 sees through p@f7 to the valuable n@g8 behind it",
          "source": {
            "theme": "x_ray",
            "squares": [
              "c4",
              "f7",
              "g8"
            ],
            "pieces": [
              "B@c4"
            ],
            "confidence": 0.6
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Weakens opponent king: opponent king safety drops from -1.00 to -2.00.",
          "evidence": "opponent king safety drops from -1.00 to -2.00",
          "source": {
            "theme": "weakens_opponent_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bishop pair: the mover owns both bishops.",
          "evidence": "the mover owns both bishops",
          "source": {
            "theme": "bishop_pair",
            "squares": [
              "c1",
              "c4"
            ],
            "pieces": [
              "B@c1",
              "B@c4"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Develops piece: B@c4 develops off the back rank.",
          "evidence": "B@c4 develops off the back rank",
          "source": {
            "theme": "develops_piece",
            "squares": [
              "f1",
              "c4"
            ],
            "pieces": [
              "B@c4"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Mobility: improved by 30.0.",
          "evidence": "positional_delta.mobility=30.0",
          "source": {
            "group": "mobility",
            "value": 30.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Activity: improved by 7.5.",
          "evidence": "positional_delta.activity=7.5",
          "source": {
            "group": "activity",
            "value": 7.5
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 improves piece: the B moves toward the centre.",
          "evidence": "the B moves toward the centre",
          "source": {
            "tag": "improves_piece",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 develops: develops the B to c4.",
          "evidence": "develops the B to c4",
          "source": {
            "tag": "develops",
            "moves": [],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 attacks king: pressure on the enemy king rises.",
          "evidence": "pressure on the enemy king rises",
          "source": {
            "tag": "attacks_king",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "engine",
          "text": "The engine preferred Qb3.",
          "evidence": "best_move=f3b3, label=good",
          "source": {
            "best_move": "f3b3",
            "label": "good"
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 11,
      "move_san": "Nf6",
      "move_uci": "g8f6",
      "headline": "Nf6 \u2014 a mistake.",
      "sentences": [
        "It gives up 1.53 pawns (12% win probability).",
        "The position was critical: small differences in the evaluation mattered.",
        "Interference: n@f6 interposes on the Q@f3's line, denying the capture on f7.",
        "Develops piece: n@f6 develops off the back rank.",
        "Controls center: central control rises from 2.00 to 3.00.",
        "Mobility: improved by 6.0.",
        "Space: improved by 4.0.",
        "Activity: improved by 10.0.",
        "Intent \u2014 improves piece: the n moves toward the centre.",
        "Intent \u2014 restricts opponent: opponent mobility drops from 34.0 to 33.0.",
        "Intent \u2014 develops: develops the n to f6.",
        "The engine preferred Qd7."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "Nf6 \u2014 a mistake.",
          "evidence": "quality.label=mistake",
          "source": {
            "move_san": "Nf6",
            "label": "mistake"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "It gives up 1.53 pawns (12% win probability).",
          "evidence": "eval_before_cp=-138.0, eval_after_cp=-291.0, loss_cp=153.0, loss_wp=0.121",
          "source": {
            "label": "mistake",
            "eval_after_cp": -291.0,
            "loss_cp": 153.0,
            "loss_wp": 0.1205119659913304
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "The position was critical: small differences in the evaluation mattered.",
          "evidence": "is_critical=True, sharpness=0.034",
          "source": {
            "flag": "is_critical",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Interference: n@f6 interposes on the Q@f3's line, denying the capture on f7.",
          "evidence": "n@f6 interposes on the Q@f3's line, denying the capture on f7",
          "source": {
            "theme": "interference",
            "squares": [
              "f3",
              "f6",
              "f7"
            ],
            "pieces": [
              "Q@f3",
              "n@f6"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Develops piece: n@f6 develops off the back rank.",
          "evidence": "n@f6 develops off the back rank",
          "source": {
            "theme": "develops_piece",
            "squares": [
              "g8",
              "f6"
            ],
            "pieces": [
              "n@f6"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Controls center: central control rises from 2.00 to 3.00.",
          "evidence": "central control rises from 2.00 to 3.00",
          "source": {
            "theme": "controls_center",
            "squares": [],
            "pieces": [],
            "confidence": 0.8
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Mobility: improved by 6.0.",
          "evidence": "positional_delta.mobility=6.0",
          "source": {
            "group": "mobility",
            "value": 6.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Space: improved by 4.0.",
          "evidence": "positional_delta.space=4.0",
          "source": {
            "group": "space",
            "value": 4.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Activity: improved by 10.0.",
          "evidence": "positional_delta.activity=10.0",
          "source": {
            "group": "activity",
            "value": 10.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 improves piece: the n moves toward the centre.",
          "evidence": "the n moves toward the centre",
          "source": {
            "tag": "improves_piece",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 restricts opponent: opponent mobility drops from 34.0 to 33.0.",
          "evidence": "opponent mobility drops from 34.0 to 33.0",
          "source": {
            "tag": "restricts_opponent",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 develops: develops the n to f6.",
          "evidence": "develops the n to f6",
          "source": {
            "tag": "develops",
            "moves": [],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "engine",
          "text": "The engine preferred Qd7.",
          "evidence": "best_move=d8d7, label=mistake",
          "source": {
            "best_move": "d8d7",
            "label": "mistake"
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 12,
      "move_san": "Qb3",
      "move_uci": "f3b3",
      "headline": "Qb3 \u2014 the best move.",
      "sentences": [
        "The evaluation remains +2.56 for the mover.",
        "X ray: Q@b3 sees through p@b7 to the valuable n@b8 behind it.",
        "Bishop pair: the mover owns both bishops.",
        "Mobility: worsened by 18.0.",
        "Space: worsened by 4.0."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "Qb3 \u2014 the best move.",
          "evidence": "quality.label=best",
          "source": {
            "move_san": "Qb3",
            "label": "best"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "The evaluation remains +2.56 for the mover.",
          "evidence": "eval_before_cp=256.0, eval_after_cp=256.0, loss_cp=0.0, loss_wp=0.000",
          "source": {
            "label": "best",
            "eval_after_cp": 256.0,
            "loss_cp": 0.0,
            "loss_wp": 0.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "X ray: Q@b3 sees through p@b7 to the valuable n@b8 behind it.",
          "evidence": "Q@b3 sees through p@b7 to the valuable n@b8 behind it",
          "source": {
            "theme": "x_ray",
            "squares": [
              "b3",
              "b7",
              "b8"
            ],
            "pieces": [
              "Q@b3"
            ],
            "confidence": 0.6
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bishop pair: the mover owns both bishops.",
          "evidence": "the mover owns both bishops",
          "source": {
            "theme": "bishop_pair",
            "squares": [
              "c1",
              "c4"
            ],
            "pieces": [
              "B@c1",
              "B@c4"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Mobility: worsened by 18.0.",
          "evidence": "positional_delta.mobility=-18.0",
          "source": {
            "group": "mobility",
            "value": -18.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Space: worsened by 4.0.",
          "evidence": "positional_delta.space=-4.0",
          "source": {
            "group": "space",
            "value": -4.0
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 13,
      "move_san": "Qe7",
      "move_uci": "d8e7",
      "headline": "Qe7 \u2014 a good move.",
      "sentences": [
        "It gives up 0.43 pawns (3% win probability).",
        "Bad bishop: bishop on f8 is blocked by its own pawns.",
        "Controls center: central control rises from 3.00 to 4.00.",
        "Mobility: worsened by 42.0.",
        "Space: improved by 4.0.",
        "Intent \u2014 improves piece: the q moves toward the centre.",
        "The engine preferred Bc5."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "Qe7 \u2014 a good move.",
          "evidence": "quality.label=good",
          "source": {
            "move_san": "Qe7",
            "label": "good"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "It gives up 0.43 pawns (3% win probability).",
          "evidence": "eval_before_cp=-256.0, eval_after_cp=-299.0, loss_cp=43.0, loss_wp=0.031",
          "source": {
            "label": "good",
            "eval_after_cp": -299.0,
            "loss_cp": 43.0,
            "loss_wp": 0.030809487407843034
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bad bishop: bishop on f8 is blocked by its own pawns.",
          "evidence": "bishop on f8 is blocked by its own pawns",
          "source": {
            "theme": "bad_bishop",
            "squares": [
              "f8"
            ],
            "pieces": [
              "b@f8"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Controls center: central control rises from 3.00 to 4.00.",
          "evidence": "central control rises from 3.00 to 4.00",
          "source": {
            "theme": "controls_center",
            "squares": [],
            "pieces": [],
            "confidence": 0.8
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Mobility: worsened by 42.0.",
          "evidence": "positional_delta.mobility=-42.0",
          "source": {
            "group": "mobility",
            "value": -42.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Space: improved by 4.0.",
          "evidence": "positional_delta.space=4.0",
          "source": {
            "group": "space",
            "value": 4.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 improves piece: the q moves toward the centre.",
          "evidence": "the q moves toward the centre",
          "source": {
            "tag": "improves_piece",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "engine",
          "text": "The engine preferred Bc5.",
          "evidence": "best_move=f8c5, label=good",
          "source": {
            "best_move": "f8c5",
            "label": "good"
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 14,
      "move_san": "Nc3",
      "move_uci": "b1c3",
      "headline": "Nc3 \u2014 a good move.",
      "sentences": [
        "It gives up 0.62 pawns (5% win probability).",
        "X ray: Q@b3 sees through p@b7 to the valuable n@b8 behind it.",
        "Bishop pair: the mover owns both bishops.",
        "Develops piece: N@c3 develops off the back rank.",
        "Controls center: central control rises from 1.00 to 2.00.",
        "Mobility: worsened by 12.0.",
        "Space: improved by 4.0.",
        "Activity: improved by 10.0.",
        "Intent \u2014 improves piece: the N moves toward the centre.",
        "Intent \u2014 develops: develops the N to c3.",
        "The engine preferred Qxb7."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "Nc3 \u2014 a good move.",
          "evidence": "quality.label=good",
          "source": {
            "move_san": "Nc3",
            "label": "good"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "It gives up 0.62 pawns (5% win probability).",
          "evidence": "eval_before_cp=299.0, eval_after_cp=237.0, loss_cp=62.0, loss_wp=0.045",
          "source": {
            "label": "good",
            "eval_after_cp": 237.0,
            "loss_cp": 62.0,
            "loss_wp": 0.04513912764724115
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "X ray: Q@b3 sees through p@b7 to the valuable n@b8 behind it.",
          "evidence": "Q@b3 sees through p@b7 to the valuable n@b8 behind it",
          "source": {
            "theme": "x_ray",
            "squares": [
              "b3",
              "b7",
              "b8"
            ],
            "pieces": [
              "Q@b3"
            ],
            "confidence": 0.6
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bishop pair: the mover owns both bishops.",
          "evidence": "the mover owns both bishops",
          "source": {
            "theme": "bishop_pair",
            "squares": [
              "c1",
              "c4"
            ],
            "pieces": [
              "B@c1",
              "B@c4"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Develops piece: N@c3 develops off the back rank.",
          "evidence": "N@c3 develops off the back rank",
          "source": {
            "theme": "develops_piece",
            "squares": [
              "b1",
              "c3"
            ],
            "pieces": [
              "N@c3"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Controls center: central control rises from 1.00 to 2.00.",
          "evidence": "central control rises from 1.00 to 2.00",
          "source": {
            "theme": "controls_center",
            "squares": [],
            "pieces": [],
            "confidence": 0.8
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Mobility: worsened by 12.0.",
          "evidence": "positional_delta.mobility=-12.0",
          "source": {
            "group": "mobility",
            "value": -12.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Space: improved by 4.0.",
          "evidence": "positional_delta.space=4.0",
          "source": {
            "group": "space",
            "value": 4.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Activity: improved by 10.0.",
          "evidence": "positional_delta.activity=10.0",
          "source": {
            "group": "activity",
            "value": 10.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 improves piece: the N moves toward the centre.",
          "evidence": "the N moves toward the centre",
          "source": {
            "tag": "improves_piece",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 develops: develops the N to c3.",
          "evidence": "develops the N to c3",
          "source": {
            "tag": "develops",
            "moves": [],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "engine",
          "text": "The engine preferred Qxb7.",
          "evidence": "best_move=b3b7, label=good",
          "source": {
            "best_move": "b3b7",
            "label": "good"
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 15,
      "move_san": "c6",
      "move_uci": "c7c6",
      "headline": "c6 \u2014 the best move.",
      "sentences": [
        "The evaluation remains -2.35 for the mover.",
        "Bad bishop: bishop on f8 is blocked by its own pawns."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "c6 \u2014 the best move.",
          "evidence": "quality.label=best",
          "source": {
            "move_san": "c6",
            "label": "best"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "The evaluation remains -2.35 for the mover.",
          "evidence": "eval_before_cp=-235.0, eval_after_cp=-235.0, loss_cp=0.0, loss_wp=0.000",
          "source": {
            "label": "best",
            "eval_after_cp": -235.0,
            "loss_cp": 0.0,
            "loss_wp": 0.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bad bishop: bishop on f8 is blocked by its own pawns.",
          "evidence": "bishop on f8 is blocked by its own pawns",
          "source": {
            "theme": "bad_bishop",
            "squares": [
              "f8"
            ],
            "pieces": [
              "b@f8"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 16,
      "move_san": "Bg5",
      "move_uci": "c1g5",
      "headline": "Bg5 \u2014 the best move.",
      "sentences": [
        "The evaluation remains +2.44 for the mover.",
        "Threat created: the move now attacks the defended n@f6.",
        "X ray: B@g5 sees through n@f6 to the valuable q@e7 behind it.",
        "Weakens opponent king: opponent king safety drops from -1.00 to -2.00.",
        "Bishop pair: the mover owns both bishops.",
        "Develops piece: B@g5 develops off the back rank.",
        "Mobility: improved by 24.0.",
        "Activity: improved by 5.0.",
        "Intent \u2014 improves piece: the B moves toward the centre.",
        "Intent \u2014 develops: develops the B to g5.",
        "Intent \u2014 attacks king: pressure on the enemy king rises."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "Bg5 \u2014 the best move.",
          "evidence": "quality.label=best",
          "source": {
            "move_san": "Bg5",
            "label": "best"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "The evaluation remains +2.44 for the mover.",
          "evidence": "eval_before_cp=244.0, eval_after_cp=244.0, loss_cp=0.0, loss_wp=0.000",
          "source": {
            "label": "best",
            "eval_after_cp": 244.0,
            "loss_cp": 0.0,
            "loss_wp": 0.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Threat created: the move now attacks the defended n@f6.",
          "evidence": "the move now attacks the defended n@f6",
          "source": {
            "theme": "threat_created",
            "squares": [
              "f6"
            ],
            "pieces": [
              "n@f6",
              "B@g5"
            ],
            "confidence": 0.8
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "X ray: B@g5 sees through n@f6 to the valuable q@e7 behind it.",
          "evidence": "B@g5 sees through n@f6 to the valuable q@e7 behind it",
          "source": {
            "theme": "x_ray",
            "squares": [
              "g5",
              "f6",
              "e7"
            ],
            "pieces": [
              "B@g5"
            ],
            "confidence": 0.6
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Weakens opponent king: opponent king safety drops from -1.00 to -2.00.",
          "evidence": "opponent king safety drops from -1.00 to -2.00",
          "source": {
            "theme": "weakens_opponent_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bishop pair: the mover owns both bishops.",
          "evidence": "the mover owns both bishops",
          "source": {
            "theme": "bishop_pair",
            "squares": [
              "c4",
              "g5"
            ],
            "pieces": [
              "B@c4",
              "B@g5"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Develops piece: B@g5 develops off the back rank.",
          "evidence": "B@g5 develops off the back rank",
          "source": {
            "theme": "develops_piece",
            "squares": [
              "c1",
              "g5"
            ],
            "pieces": [
              "B@g5"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Mobility: improved by 24.0.",
          "evidence": "positional_delta.mobility=24.0",
          "source": {
            "group": "mobility",
            "value": 24.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Activity: improved by 5.0.",
          "evidence": "positional_delta.activity=5.0",
          "source": {
            "group": "activity",
            "value": 5.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 improves piece: the B moves toward the centre.",
          "evidence": "the B moves toward the centre",
          "source": {
            "tag": "improves_piece",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 develops: develops the B to g5.",
          "evidence": "develops the B to g5",
          "source": {
            "tag": "develops",
            "moves": [],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 attacks king: pressure on the enemy king rises.",
          "evidence": "pressure on the enemy king rises",
          "source": {
            "tag": "attacks_king",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 17,
      "move_san": "b5",
      "move_uci": "b7b5",
      "headline": "b5 \u2014 a mistake.",
      "sentences": [
        "It gives up 1.97 pawns (12% win probability).",
        "The position was critical: small differences in the evaluation mattered.",
        "Pin: the cheap p@b5 holds the defended B@c4 in place.",
        "Threat created: the move now attacks the defended B@c4.",
        "Interference: p@b5 interposes on the Q@b3's line, denying the capture on b7.",
        "Bad bishop: bishop on f8 is blocked by its own pawns.",
        "Mobility: improved by 6.0.",
        "Intent \u2014 restricts opponent: opponent mobility drops from 32.0 to 29.0.",
        "The engine preferred Na6."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "b5 \u2014 a mistake.",
          "evidence": "quality.label=mistake",
          "source": {
            "move_san": "b5",
            "label": "mistake"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "It gives up 1.97 pawns (12% win probability).",
          "evidence": "eval_before_cp=-262.0, eval_after_cp=-459.0, loss_cp=197.0, loss_wp=0.120",
          "source": {
            "label": "mistake",
            "eval_after_cp": -459.0,
            "loss_cp": 197.0,
            "loss_wp": 0.12017115912996162
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "The position was critical: small differences in the evaluation mattered.",
          "evidence": "is_critical=True, sharpness=0.026",
          "source": {
            "flag": "is_critical",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Pin: the cheap p@b5 holds the defended B@c4 in place.",
          "evidence": "the cheap p@b5 holds the defended B@c4 in place",
          "source": {
            "theme": "pin",
            "squares": [
              "c4"
            ],
            "pieces": [
              "B@c4",
              "p@b5"
            ],
            "confidence": 0.6
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Threat created: the move now attacks the defended B@c4.",
          "evidence": "the move now attacks the defended B@c4",
          "source": {
            "theme": "threat_created",
            "squares": [
              "c4"
            ],
            "pieces": [
              "B@c4",
              "p@b5"
            ],
            "confidence": 0.8
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Interference: p@b5 interposes on the Q@b3's line, denying the capture on b7.",
          "evidence": "p@b5 interposes on the Q@b3's line, denying the capture on b7",
          "source": {
            "theme": "interference",
            "squares": [
              "b3",
              "b5",
              "b7"
            ],
            "pieces": [
              "Q@b3",
              "p@b5"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bad bishop: bishop on f8 is blocked by its own pawns.",
          "evidence": "bishop on f8 is blocked by its own pawns",
          "source": {
            "theme": "bad_bishop",
            "squares": [
              "f8"
            ],
            "pieces": [
              "b@f8"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Mobility: improved by 6.0.",
          "evidence": "positional_delta.mobility=6.0",
          "source": {
            "group": "mobility",
            "value": 6.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 restricts opponent: opponent mobility drops from 32.0 to 29.0.",
          "evidence": "opponent mobility drops from 32.0 to 29.0",
          "source": {
            "tag": "restricts_opponent",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "engine",
          "text": "The engine preferred Na6.",
          "evidence": "best_move=b8a6, label=mistake",
          "source": {
            "best_move": "b8a6",
            "label": "mistake"
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 18,
      "move_san": "Nxb5",
      "move_uci": "c3b5",
      "headline": "Nxb5 \u2014 a great move.",
      "sentences": [
        "The evaluation remains +4.46 for the mover.",
        "It was the only move that keeps the position.",
        "The move is forcing: a check or a forced mate.",
        "The position was critical: small differences in the evaluation mattered.",
        "X ray: B@g5 sees through n@f6 to the valuable q@e7 behind it.",
        "Capture: takes the p@b5.",
        "Sacrifice: gives up the N@c3 for the p@b5.",
        "Weakens opponent king: opponent king safety drops from -2.00 to -3.00.",
        "Bishop pair: the mover owns both bishops.",
        "Material: the mover gained 1.00 pawns.",
        "Mobility: improved by 24.0.",
        "Activity: worsened by 5.0.",
        "Intent \u2014 attacks king: pressure on the enemy king rises."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "Nxb5 \u2014 a great move.",
          "evidence": "quality.label=great",
          "source": {
            "move_san": "Nxb5",
            "label": "great"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "The evaluation remains +4.46 for the mover.",
          "evidence": "eval_before_cp=446.0, eval_after_cp=446.0, loss_cp=0.0, loss_wp=0.000",
          "source": {
            "label": "great",
            "eval_after_cp": 446.0,
            "loss_cp": 0.0,
            "loss_wp": 0.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "It was the only move that keeps the position.",
          "evidence": "is_only_move=True, gap_to_second_wp=0.227",
          "source": {
            "flag": "is_only_move",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "The move is forcing: a check or a forced mate.",
          "evidence": "is_forcing=True",
          "source": {
            "flag": "is_forcing",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "The position was critical: small differences in the evaluation mattered.",
          "evidence": "is_critical=True, sharpness=0.261",
          "source": {
            "flag": "is_critical",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "X ray: B@g5 sees through n@f6 to the valuable q@e7 behind it.",
          "evidence": "B@g5 sees through n@f6 to the valuable q@e7 behind it",
          "source": {
            "theme": "x_ray",
            "squares": [
              "g5",
              "f6",
              "e7"
            ],
            "pieces": [
              "B@g5"
            ],
            "confidence": 0.6
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Capture: takes the p@b5.",
          "evidence": "takes the p@b5",
          "source": {
            "theme": "capture",
            "squares": [
              "c3",
              "b5"
            ],
            "pieces": [
              "N@b5"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Sacrifice: gives up the N@c3 for the p@b5.",
          "evidence": "gives up the N@c3 for the p@b5",
          "source": {
            "theme": "sacrifice",
            "squares": [
              "c3",
              "b5"
            ],
            "pieces": [
              "N@b5"
            ],
            "confidence": 0.8
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Weakens opponent king: opponent king safety drops from -2.00 to -3.00.",
          "evidence": "opponent king safety drops from -2.00 to -3.00",
          "source": {
            "theme": "weakens_opponent_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bishop pair: the mover owns both bishops.",
          "evidence": "the mover owns both bishops",
          "source": {
            "theme": "bishop_pair",
            "squares": [
              "c4",
              "g5"
            ],
            "pieces": [
              "B@c4",
              "B@g5"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Material: the mover gained 1.00 pawns.",
          "evidence": "positional_delta.material=100.0",
          "source": {
            "group": "material",
            "value": 100.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Mobility: improved by 24.0.",
          "evidence": "positional_delta.mobility=24.0",
          "source": {
            "group": "mobility",
            "value": 24.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Activity: worsened by 5.0.",
          "evidence": "positional_delta.activity=-5.0",
          "source": {
            "group": "activity",
            "value": -5.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 attacks king: pressure on the enemy king rises.",
          "evidence": "pressure on the enemy king rises",
          "source": {
            "tag": "attacks_king",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 19,
      "move_san": "cxb5",
      "move_uci": "c6b5",
      "headline": "cxb5 \u2014 an inaccuracy.",
      "sentences": [
        "It gives up 1.56 pawns (7% win probability).",
        "The move is forcing: a check or a forced mate.",
        "Pin: the cheap p@b5 holds the defended B@c4 in place.",
        "Threat created: the move now attacks the defended B@c4.",
        "Capture: takes the N@b5.",
        "Shelters king: king safety rises from -3.00 to -2.00.",
        "Pawn island: pawn island count changes from 3 to 2.",
        "Bad bishop: bishop on f8 is blocked by its own pawns.",
        "Material: the mover gained 3.20 pawns.",
        "Mobility: improved by 6.0.",
        "King safety: improved by 12.0.",
        "Pawn structure: improved by 30.0.",
        "Intent \u2014 restricts opponent: opponent mobility drops from 33.0 to 29.0.",
        "The engine preferred Qb4+."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "cxb5 \u2014 an inaccuracy.",
          "evidence": "quality.label=inaccuracy",
          "source": {
            "move_san": "cxb5",
            "label": "inaccuracy"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "It gives up 1.56 pawns (7% win probability).",
          "evidence": "eval_before_cp=-433.0, eval_after_cp=-589.0, loss_cp=156.0, loss_wp=0.066",
          "source": {
            "label": "inaccuracy",
            "eval_after_cp": -589.0,
            "loss_cp": 156.0,
            "loss_wp": 0.06618156616948516
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "The move is forcing: a check or a forced mate.",
          "evidence": "is_forcing=True",
          "source": {
            "flag": "is_forcing",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Pin: the cheap p@b5 holds the defended B@c4 in place.",
          "evidence": "the cheap p@b5 holds the defended B@c4 in place",
          "source": {
            "theme": "pin",
            "squares": [
              "c4"
            ],
            "pieces": [
              "B@c4",
              "p@b5"
            ],
            "confidence": 0.6
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Threat created: the move now attacks the defended B@c4.",
          "evidence": "the move now attacks the defended B@c4",
          "source": {
            "theme": "threat_created",
            "squares": [
              "c4"
            ],
            "pieces": [
              "B@c4",
              "p@b5"
            ],
            "confidence": 0.8
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Capture: takes the N@b5.",
          "evidence": "takes the N@b5",
          "source": {
            "theme": "capture",
            "squares": [
              "c6",
              "b5"
            ],
            "pieces": [
              "p@b5"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Shelters king: king safety rises from -3.00 to -2.00.",
          "evidence": "king safety rises from -3.00 to -2.00",
          "source": {
            "theme": "shelters_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Pawn island: pawn island count changes from 3 to 2.",
          "evidence": "pawn island count changes from 3 to 2",
          "source": {
            "theme": "pawn_island",
            "squares": [],
            "pieces": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bad bishop: bishop on f8 is blocked by its own pawns.",
          "evidence": "bishop on f8 is blocked by its own pawns",
          "source": {
            "theme": "bad_bishop",
            "squares": [
              "f8"
            ],
            "pieces": [
              "b@f8"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Material: the mover gained 3.20 pawns.",
          "evidence": "positional_delta.material=320.0",
          "source": {
            "group": "material",
            "value": 320.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Mobility: improved by 6.0.",
          "evidence": "positional_delta.mobility=6.0",
          "source": {
            "group": "mobility",
            "value": 6.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "King safety: improved by 12.0.",
          "evidence": "positional_delta.king_safety=12.0",
          "source": {
            "group": "king_safety",
            "value": 12.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Pawn structure: improved by 30.0.",
          "evidence": "positional_delta.pawn_structure=30.0",
          "source": {
            "group": "pawn_structure",
            "value": 30.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 restricts opponent: opponent mobility drops from 33.0 to 29.0.",
          "evidence": "opponent mobility drops from 33.0 to 29.0",
          "source": {
            "tag": "restricts_opponent",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "engine",
          "text": "The engine preferred Qb4+.",
          "evidence": "best_move=e7b4, label=inaccuracy",
          "source": {
            "best_move": "e7b4",
            "label": "inaccuracy"
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 20,
      "move_san": "Bxb5+",
      "move_uci": "c4b5",
      "headline": "Bxb5+ \u2014 a great move.",
      "sentences": [
        "The evaluation remains +6.18 for the mover.",
        "It was the only move that keeps the position.",
        "The move is forcing: a check or a forced mate.",
        "The position was critical: small differences in the evaluation mattered.",
        "Trapped piece: n@f6 is attacked and every square it can reach is covered too.",
        "X ray: B@g5 sees through n@f6 to the valuable q@e7 behind it.",
        "Capture: takes the p@b5.",
        "Weakens opponent king: opponent king safety drops from -2.00 to -4.00.",
        "Passed pawn: passed pawn on c2.",
        "Creates passed pawn: the move creates a passed pawn on c2.",
        "Bishop pair: the mover owns both bishops.",
        "Material: the mover gained 1.00 pawns.",
        "Mobility: improved by 30.0.",
        "Pawn structure: improved by 25.0.",
        "Intent \u2014 attacks king: Bxb5+ gives check."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "Bxb5+ \u2014 a great move.",
          "evidence": "quality.label=great",
          "source": {
            "move_san": "Bxb5+",
            "label": "great"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "The evaluation remains +6.18 for the mover.",
          "evidence": "eval_before_cp=618.0, eval_after_cp=618.0, loss_cp=0.0, loss_wp=0.000",
          "source": {
            "label": "great",
            "eval_after_cp": 618.0,
            "loss_cp": 0.0,
            "loss_wp": 0.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "It was the only move that keeps the position.",
          "evidence": "is_only_move=True, gap_to_second_wp=0.282",
          "source": {
            "flag": "is_only_move",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "The move is forcing: a check or a forced mate.",
          "evidence": "is_forcing=True",
          "source": {
            "flag": "is_forcing",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "The position was critical: small differences in the evaluation mattered.",
          "evidence": "is_critical=True, sharpness=0.560",
          "source": {
            "flag": "is_critical",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Trapped piece: n@f6 is attacked and every square it can reach is covered too.",
          "evidence": "n@f6 is attacked and every square it can reach is covered too",
          "source": {
            "theme": "trapped_piece",
            "squares": [
              "f6"
            ],
            "pieces": [
              "n@f6"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "X ray: B@g5 sees through n@f6 to the valuable q@e7 behind it.",
          "evidence": "B@g5 sees through n@f6 to the valuable q@e7 behind it",
          "source": {
            "theme": "x_ray",
            "squares": [
              "g5",
              "f6",
              "e7"
            ],
            "pieces": [
              "B@g5"
            ],
            "confidence": 0.6
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Capture: takes the p@b5.",
          "evidence": "takes the p@b5",
          "source": {
            "theme": "capture",
            "squares": [
              "c4",
              "b5"
            ],
            "pieces": [
              "B@b5"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Weakens opponent king: opponent king safety drops from -2.00 to -4.00.",
          "evidence": "opponent king safety drops from -2.00 to -4.00",
          "source": {
            "theme": "weakens_opponent_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Passed pawn: passed pawn on c2.",
          "evidence": "passed pawn on c2",
          "source": {
            "theme": "passed_pawn",
            "squares": [
              "c2"
            ],
            "pieces": [
              "P@c2"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Creates passed pawn: the move creates a passed pawn on c2.",
          "evidence": "the move creates a passed pawn on c2",
          "source": {
            "theme": "creates_passed_pawn",
            "squares": [
              "c2"
            ],
            "pieces": [
              "P@c2"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bishop pair: the mover owns both bishops.",
          "evidence": "the mover owns both bishops",
          "source": {
            "theme": "bishop_pair",
            "squares": [
              "b5",
              "g5"
            ],
            "pieces": [
              "B@b5",
              "B@g5"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Material: the mover gained 1.00 pawns.",
          "evidence": "positional_delta.material=100.0",
          "source": {
            "group": "material",
            "value": 100.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Mobility: improved by 30.0.",
          "evidence": "positional_delta.mobility=30.0",
          "source": {
            "group": "mobility",
            "value": 30.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Pawn structure: improved by 25.0.",
          "evidence": "positional_delta.pawn_structure=25.0",
          "source": {
            "group": "pawn_structure",
            "value": 25.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 attacks king: Bxb5+ gives check.",
          "evidence": "Bxb5+ gives check",
          "source": {
            "tag": "attacks_king",
            "moves": [],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 21,
      "move_san": "Nbd7",
      "move_uci": "b8d7",
      "headline": "Nbd7 \u2014 the best move.",
      "sentences": [
        "The evaluation remains -5.87 for the mover.",
        "Interference: n@d7 interposes on the B@b5's line, denying the capture on e8.",
        "Shelters king: king safety rises from -4.00 to -3.00.",
        "Isolated pawn: isolated pawn on a7.",
        "Bad bishop: bishop on f8 is blocked by its own pawns.",
        "Develops piece: n@d7 develops off the back rank.",
        "Mobility: worsened by 6.0.",
        "King safety: improved by 12.0.",
        "Activity: improved by 5.0.",
        "Intent \u2014 improves piece: the n moves toward the centre.",
        "Intent \u2014 restricts opponent: opponent mobility drops from 34.0 to 33.0.",
        "Intent \u2014 develops: develops the n to d7."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "Nbd7 \u2014 the best move.",
          "evidence": "quality.label=best",
          "source": {
            "move_san": "Nbd7",
            "label": "best"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "The evaluation remains -5.87 for the mover.",
          "evidence": "eval_before_cp=-587.0, eval_after_cp=-587.0, loss_cp=0.0, loss_wp=0.000",
          "source": {
            "label": "best",
            "eval_after_cp": -587.0,
            "loss_cp": 0.0,
            "loss_wp": 0.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Interference: n@d7 interposes on the B@b5's line, denying the capture on e8.",
          "evidence": "n@d7 interposes on the B@b5's line, denying the capture on e8",
          "source": {
            "theme": "interference",
            "squares": [
              "b5",
              "d7",
              "e8"
            ],
            "pieces": [
              "B@b5",
              "n@d7"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Shelters king: king safety rises from -4.00 to -3.00.",
          "evidence": "king safety rises from -4.00 to -3.00",
          "source": {
            "theme": "shelters_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Isolated pawn: isolated pawn on a7.",
          "evidence": "isolated pawn on a7",
          "source": {
            "theme": "isolated_pawn",
            "squares": [
              "a7"
            ],
            "pieces": [
              "p@a7"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bad bishop: bishop on f8 is blocked by its own pawns.",
          "evidence": "bishop on f8 is blocked by its own pawns",
          "source": {
            "theme": "bad_bishop",
            "squares": [
              "f8"
            ],
            "pieces": [
              "b@f8"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Develops piece: n@d7 develops off the back rank.",
          "evidence": "n@d7 develops off the back rank",
          "source": {
            "theme": "develops_piece",
            "squares": [
              "b8",
              "d7"
            ],
            "pieces": [
              "n@d7"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Mobility: worsened by 6.0.",
          "evidence": "positional_delta.mobility=-6.0",
          "source": {
            "group": "mobility",
            "value": -6.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "King safety: improved by 12.0.",
          "evidence": "positional_delta.king_safety=12.0",
          "source": {
            "group": "king_safety",
            "value": 12.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Activity: improved by 5.0.",
          "evidence": "positional_delta.activity=5.0",
          "source": {
            "group": "activity",
            "value": 5.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 improves piece: the n moves toward the centre.",
          "evidence": "the n moves toward the centre",
          "source": {
            "tag": "improves_piece",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 restricts opponent: opponent mobility drops from 34.0 to 33.0.",
          "evidence": "opponent mobility drops from 34.0 to 33.0",
          "source": {
            "tag": "restricts_opponent",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 develops: develops the n to d7.",
          "evidence": "develops the n to d7",
          "source": {
            "tag": "develops",
            "moves": [],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 22,
      "move_san": "O-O-O",
      "move_uci": "e1c1",
      "headline": "O-O-O \u2014 the best move.",
      "sentences": [
        "The evaluation remains +5.75 for the mover.",
        "Pin: n@d7 cannot move without exposing its own king.",
        "X ray: B@g5 sees through n@f6 to the valuable q@e7 behind it.",
        "Shelters king: king safety rises from 1.00 to 2.00.",
        "Weakens opponent king: opponent king safety drops from -3.00 to -4.00.",
        "Passed pawn: passed pawn on c2.",
        "Bishop pair: the mover owns both bishops.",
        "Controls center: central control rises from 1.00 to 2.00.",
        "Mobility: improved by 36.0.",
        "King safety: improved by 12.0.",
        "Space: improved by 4.0.",
        "Activity: improved by 5.0.",
        "Intent \u2014 castles: the move castles.",
        "Intent \u2014 attacks king: pressure on the enemy king rises."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "O-O-O \u2014 the best move.",
          "evidence": "quality.label=best",
          "source": {
            "move_san": "O-O-O",
            "label": "best"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "The evaluation remains +5.75 for the mover.",
          "evidence": "eval_before_cp=575.0, eval_after_cp=575.0, loss_cp=0.0, loss_wp=0.000",
          "source": {
            "label": "best",
            "eval_after_cp": 575.0,
            "loss_cp": 0.0,
            "loss_wp": 0.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Pin: n@d7 cannot move without exposing its own king.",
          "evidence": "n@d7 cannot move without exposing its own king",
          "source": {
            "theme": "pin",
            "squares": [
              "d7"
            ],
            "pieces": [
              "n@d7"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "X ray: B@g5 sees through n@f6 to the valuable q@e7 behind it.",
          "evidence": "B@g5 sees through n@f6 to the valuable q@e7 behind it",
          "source": {
            "theme": "x_ray",
            "squares": [
              "g5",
              "f6",
              "e7"
            ],
            "pieces": [
              "B@g5"
            ],
            "confidence": 0.6
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Shelters king: king safety rises from 1.00 to 2.00.",
          "evidence": "king safety rises from 1.00 to 2.00",
          "source": {
            "theme": "shelters_king",
            "squares": [
              "c1"
            ],
            "pieces": [
              "K@c1"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Weakens opponent king: opponent king safety drops from -3.00 to -4.00.",
          "evidence": "opponent king safety drops from -3.00 to -4.00",
          "source": {
            "theme": "weakens_opponent_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Passed pawn: passed pawn on c2.",
          "evidence": "passed pawn on c2",
          "source": {
            "theme": "passed_pawn",
            "squares": [
              "c2"
            ],
            "pieces": [
              "P@c2"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bishop pair: the mover owns both bishops.",
          "evidence": "the mover owns both bishops",
          "source": {
            "theme": "bishop_pair",
            "squares": [
              "b5",
              "g5"
            ],
            "pieces": [
              "B@b5",
              "B@g5"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Controls center: central control rises from 1.00 to 2.00.",
          "evidence": "central control rises from 1.00 to 2.00",
          "source": {
            "theme": "controls_center",
            "squares": [],
            "pieces": [],
            "confidence": 0.8
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Mobility: improved by 36.0.",
          "evidence": "positional_delta.mobility=36.0",
          "source": {
            "group": "mobility",
            "value": 36.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "King safety: improved by 12.0.",
          "evidence": "positional_delta.king_safety=12.0",
          "source": {
            "group": "king_safety",
            "value": 12.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Space: improved by 4.0.",
          "evidence": "positional_delta.space=4.0",
          "source": {
            "group": "space",
            "value": 4.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Activity: improved by 5.0.",
          "evidence": "positional_delta.activity=5.0",
          "source": {
            "group": "activity",
            "value": 5.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 castles: the move castles.",
          "evidence": "the move castles",
          "source": {
            "tag": "castles",
            "moves": [],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 attacks king: pressure on the enemy king rises.",
          "evidence": "pressure on the enemy king rises",
          "source": {
            "tag": "attacks_king",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 23,
      "move_san": "Rd8",
      "move_uci": "a8d8",
      "headline": "Rd8 \u2014 a good move.",
      "sentences": [
        "It gives up 1.11 pawns (3% win probability).",
        "Isolated pawn: isolated pawn on a7.",
        "Rook open file: rook on the open d-file.",
        "Bad bishop: bishop on f8 is blocked by its own pawns.",
        "Mobility: worsened by 6.0.",
        "Activity: improved by 5.0.",
        "The engine preferred Qe6."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "Rd8 \u2014 a good move.",
          "evidence": "quality.label=good",
          "source": {
            "move_san": "Rd8",
            "label": "good"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "It gives up 1.11 pawns (3% win probability).",
          "evidence": "eval_before_cp=-631.0, eval_after_cp=-742.0, loss_cp=111.0, loss_wp=0.028",
          "source": {
            "label": "good",
            "eval_after_cp": -742.0,
            "loss_cp": 111.0,
            "loss_wp": 0.02809866876837415
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Isolated pawn: isolated pawn on a7.",
          "evidence": "isolated pawn on a7",
          "source": {
            "theme": "isolated_pawn",
            "squares": [
              "a7"
            ],
            "pieces": [
              "p@a7"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Rook open file: rook on the open d-file.",
          "evidence": "rook on the open d-file",
          "source": {
            "theme": "rook_open_file",
            "squares": [
              "d8"
            ],
            "pieces": [
              "r@d8"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bad bishop: bishop on f8 is blocked by its own pawns.",
          "evidence": "bishop on f8 is blocked by its own pawns",
          "source": {
            "theme": "bad_bishop",
            "squares": [
              "f8"
            ],
            "pieces": [
              "b@f8"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Mobility: worsened by 6.0.",
          "evidence": "positional_delta.mobility=-6.0",
          "source": {
            "group": "mobility",
            "value": -6.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Activity: improved by 5.0.",
          "evidence": "positional_delta.activity=5.0",
          "source": {
            "group": "activity",
            "value": 5.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "engine",
          "text": "The engine preferred Qe6.",
          "evidence": "best_move=e7e6, label=good",
          "source": {
            "best_move": "e7e6",
            "label": "good"
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 24,
      "move_san": "Rxd7",
      "move_uci": "d1d7",
      "headline": "Rxd7 \u2014 the best move.",
      "sentences": [
        "The evaluation remains +7.28 for the mover.",
        "The move is forcing: a check or a forced mate.",
        "Pin: the cheap R@d7 holds the defended q@e7 in place.",
        "Skewer: R@d7 skewers the valuable q@e7, which must step aside and let p@f7 fall.",
        "Threat created: the move now attacks the defended q@e7.",
        "X ray: B@g5 sees through n@f6 to the valuable q@e7 behind it.",
        "Capture: takes the n@d7.",
        "Sacrifice: gives up the R@d1 for the n@d7.",
        "Weakens opponent king: opponent king safety drops from -4.00 to -6.00.",
        "Passed pawn: passed pawn on c2.",
        "Rook open file: rook on the open d-file.",
        "Rook seventh: rook reaches the seventh rank on d7.",
        "Bishop pair: the mover owns both bishops.",
        "Develops piece: R@d7 develops off the back rank.",
        "Material: the mover gained 3.20 pawns.",
        "Mobility: improved by 12.0.",
        "Intent \u2014 improves piece: the R moves toward the centre.",
        "Intent \u2014 trades defender: the move removes the defender of f6.",
        "Intent \u2014 develops: develops the R to d7.",
        "Intent \u2014 attacks king: pressure on the enemy king rises."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "Rxd7 \u2014 the best move.",
          "evidence": "quality.label=best",
          "source": {
            "move_san": "Rxd7",
            "label": "best"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "The evaluation remains +7.28 for the mover.",
          "evidence": "eval_before_cp=728.0, eval_after_cp=728.0, loss_cp=0.0, loss_wp=0.000",
          "source": {
            "label": "best",
            "eval_after_cp": 728.0,
            "loss_cp": 0.0,
            "loss_wp": 0.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "The move is forcing: a check or a forced mate.",
          "evidence": "is_forcing=True",
          "source": {
            "flag": "is_forcing",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Pin: the cheap R@d7 holds the defended q@e7 in place.",
          "evidence": "the cheap R@d7 holds the defended q@e7 in place",
          "source": {
            "theme": "pin",
            "squares": [
              "e7"
            ],
            "pieces": [
              "q@e7",
              "R@d7"
            ],
            "confidence": 0.6
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Skewer: R@d7 skewers the valuable q@e7, which must step aside and let p@f7 fall.",
          "evidence": "R@d7 skewers the valuable q@e7, which must step aside and let p@f7 fall",
          "source": {
            "theme": "skewer",
            "squares": [
              "d7",
              "e7",
              "f7"
            ],
            "pieces": [
              "R@d7"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Threat created: the move now attacks the defended q@e7.",
          "evidence": "the move now attacks the defended q@e7",
          "source": {
            "theme": "threat_created",
            "squares": [
              "e7"
            ],
            "pieces": [
              "q@e7",
              "R@d7"
            ],
            "confidence": 0.8
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "X ray: B@g5 sees through n@f6 to the valuable q@e7 behind it.",
          "evidence": "B@g5 sees through n@f6 to the valuable q@e7 behind it",
          "source": {
            "theme": "x_ray",
            "squares": [
              "g5",
              "f6",
              "e7"
            ],
            "pieces": [
              "B@g5"
            ],
            "confidence": 0.6
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Capture: takes the n@d7.",
          "evidence": "takes the n@d7",
          "source": {
            "theme": "capture",
            "squares": [
              "d1",
              "d7"
            ],
            "pieces": [
              "R@d7"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Sacrifice: gives up the R@d1 for the n@d7.",
          "evidence": "gives up the R@d1 for the n@d7",
          "source": {
            "theme": "sacrifice",
            "squares": [
              "d1",
              "d7"
            ],
            "pieces": [
              "R@d7"
            ],
            "confidence": 0.8
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Weakens opponent king: opponent king safety drops from -4.00 to -6.00.",
          "evidence": "opponent king safety drops from -4.00 to -6.00",
          "source": {
            "theme": "weakens_opponent_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Passed pawn: passed pawn on c2.",
          "evidence": "passed pawn on c2",
          "source": {
            "theme": "passed_pawn",
            "squares": [
              "c2"
            ],
            "pieces": [
              "P@c2"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Rook open file: rook on the open d-file.",
          "evidence": "rook on the open d-file",
          "source": {
            "theme": "rook_open_file",
            "squares": [
              "d7"
            ],
            "pieces": [
              "R@d7"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Rook seventh: rook reaches the seventh rank on d7.",
          "evidence": "rook reaches the seventh rank on d7",
          "source": {
            "theme": "rook_seventh",
            "squares": [
              "d7"
            ],
            "pieces": [
              "R@d7"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bishop pair: the mover owns both bishops.",
          "evidence": "the mover owns both bishops",
          "source": {
            "theme": "bishop_pair",
            "squares": [
              "b5",
              "g5"
            ],
            "pieces": [
              "B@b5",
              "B@g5"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Develops piece: R@d7 develops off the back rank.",
          "evidence": "R@d7 develops off the back rank",
          "source": {
            "theme": "develops_piece",
            "squares": [
              "d1",
              "d7"
            ],
            "pieces": [
              "R@d7"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Material: the mover gained 3.20 pawns.",
          "evidence": "positional_delta.material=320.0",
          "source": {
            "group": "material",
            "value": 320.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Mobility: improved by 12.0.",
          "evidence": "positional_delta.mobility=12.0",
          "source": {
            "group": "mobility",
            "value": 12.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 improves piece: the R moves toward the centre.",
          "evidence": "the R moves toward the centre",
          "source": {
            "tag": "improves_piece",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 trades defender: the move removes the defender of f6.",
          "evidence": "the move removes the defender of f6",
          "source": {
            "tag": "trades_defender",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 develops: develops the R to d7.",
          "evidence": "develops the R to d7",
          "source": {
            "tag": "develops",
            "moves": [],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 attacks king: pressure on the enemy king rises.",
          "evidence": "pressure on the enemy king rises",
          "source": {
            "tag": "attacks_king",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 25,
      "move_san": "Rxd7",
      "move_uci": "d8d7",
      "headline": "Rxd7 \u2014 the best move.",
      "sentences": [
        "The evaluation remains -7.21 for the mover.",
        "The move is forcing: a check or a forced mate.",
        "Capture: takes the R@d7.",
        "Shelters king: king safety rises from -6.00 to -3.00.",
        "Weakens opponent king: opponent king safety drops from 2.00 to -1.00.",
        "Isolated pawn: isolated pawn on a7.",
        "Rook open file: rook on the open d-file.",
        "Bad bishop: bishop on f8 is blocked by its own pawns.",
        "Develops piece: r@d7 develops off the back rank.",
        "Material: the mover gained 5.00 pawns.",
        "Mobility: improved by 24.0.",
        "King safety: improved by 36.0.",
        "Intent \u2014 improves piece: the r moves toward the centre.",
        "Intent \u2014 restricts opponent: opponent mobility drops from 41.0 to 31.0.",
        "Intent \u2014 develops: develops the r to d7.",
        "Intent \u2014 attacks king: pressure on the enemy king rises."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "Rxd7 \u2014 the best move.",
          "evidence": "quality.label=best",
          "source": {
            "move_san": "Rxd7",
            "label": "best"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "The evaluation remains -7.21 for the mover.",
          "evidence": "eval_before_cp=-721.0, eval_after_cp=-721.0, loss_cp=0.0, loss_wp=0.000",
          "source": {
            "label": "best",
            "eval_after_cp": -721.0,
            "loss_cp": 0.0,
            "loss_wp": 0.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "The move is forcing: a check or a forced mate.",
          "evidence": "is_forcing=True",
          "source": {
            "flag": "is_forcing",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Capture: takes the R@d7.",
          "evidence": "takes the R@d7",
          "source": {
            "theme": "capture",
            "squares": [
              "d8",
              "d7"
            ],
            "pieces": [
              "r@d7"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Shelters king: king safety rises from -6.00 to -3.00.",
          "evidence": "king safety rises from -6.00 to -3.00",
          "source": {
            "theme": "shelters_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Weakens opponent king: opponent king safety drops from 2.00 to -1.00.",
          "evidence": "opponent king safety drops from 2.00 to -1.00",
          "source": {
            "theme": "weakens_opponent_king",
            "squares": [
              "c1"
            ],
            "pieces": [
              "K@c1"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Isolated pawn: isolated pawn on a7.",
          "evidence": "isolated pawn on a7",
          "source": {
            "theme": "isolated_pawn",
            "squares": [
              "a7"
            ],
            "pieces": [
              "p@a7"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Rook open file: rook on the open d-file.",
          "evidence": "rook on the open d-file",
          "source": {
            "theme": "rook_open_file",
            "squares": [
              "d7"
            ],
            "pieces": [
              "r@d7"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bad bishop: bishop on f8 is blocked by its own pawns.",
          "evidence": "bishop on f8 is blocked by its own pawns",
          "source": {
            "theme": "bad_bishop",
            "squares": [
              "f8"
            ],
            "pieces": [
              "b@f8"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Develops piece: r@d7 develops off the back rank.",
          "evidence": "r@d7 develops off the back rank",
          "source": {
            "theme": "develops_piece",
            "squares": [
              "d8",
              "d7"
            ],
            "pieces": [
              "r@d7"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Material: the mover gained 5.00 pawns.",
          "evidence": "positional_delta.material=500.0",
          "source": {
            "group": "material",
            "value": 500.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Mobility: improved by 24.0.",
          "evidence": "positional_delta.mobility=24.0",
          "source": {
            "group": "mobility",
            "value": 24.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "King safety: improved by 36.0.",
          "evidence": "positional_delta.king_safety=36.0",
          "source": {
            "group": "king_safety",
            "value": 36.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 improves piece: the r moves toward the centre.",
          "evidence": "the r moves toward the centre",
          "source": {
            "tag": "improves_piece",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 restricts opponent: opponent mobility drops from 41.0 to 31.0.",
          "evidence": "opponent mobility drops from 41.0 to 31.0",
          "source": {
            "tag": "restricts_opponent",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 develops: develops the r to d7.",
          "evidence": "develops the r to d7",
          "source": {
            "tag": "develops",
            "moves": [],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 attacks king: pressure on the enemy king rises.",
          "evidence": "pressure on the enemy king rises",
          "source": {
            "tag": "attacks_king",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 26,
      "move_san": "Rd1",
      "move_uci": "h1d1",
      "headline": "Rd1 \u2014 a great move.",
      "sentences": [
        "The evaluation remains +7.16 for the mover.",
        "It was the only move that keeps the position.",
        "The position was critical: small differences in the evaluation mattered.",
        "Pin: r@d7 cannot move without exposing its own king.",
        "Threat created: the move now attacks the defended r@d7.",
        "X ray: B@g5 sees through n@f6 to the valuable q@e7 behind it.",
        "Weakens opponent king: opponent king safety drops from -3.00 to -4.00.",
        "Passed pawn: passed pawn on c2.",
        "Rook open file: rook on the open d-file.",
        "Bishop pair: the mover owns both bishops.",
        "Controls center: central control rises from 1.00 to 2.00.",
        "Mobility: improved by 36.0.",
        "Space: improved by 4.0.",
        "Activity: improved by 5.0.",
        "Intent \u2014 attacks king: pressure on the enemy king rises."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "Rd1 \u2014 a great move.",
          "evidence": "quality.label=great",
          "source": {
            "move_san": "Rd1",
            "label": "great"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "The evaluation remains +7.16 for the mover.",
          "evidence": "eval_before_cp=716.0, eval_after_cp=716.0, loss_cp=0.0, loss_wp=0.000",
          "source": {
            "label": "great",
            "eval_after_cp": 716.0,
            "loss_cp": 0.0,
            "loss_wp": 0.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "It was the only move that keeps the position.",
          "evidence": "is_only_move=True, gap_to_second_wp=0.193",
          "source": {
            "flag": "is_only_move",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "The position was critical: small differences in the evaluation mattered.",
          "evidence": "is_critical=True, sharpness=0.223",
          "source": {
            "flag": "is_critical",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Pin: r@d7 cannot move without exposing its own king.",
          "evidence": "r@d7 cannot move without exposing its own king",
          "source": {
            "theme": "pin",
            "squares": [
              "d7"
            ],
            "pieces": [
              "r@d7"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Threat created: the move now attacks the defended r@d7.",
          "evidence": "the move now attacks the defended r@d7",
          "source": {
            "theme": "threat_created",
            "squares": [
              "d7"
            ],
            "pieces": [
              "r@d7",
              "R@d1"
            ],
            "confidence": 0.8
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "X ray: B@g5 sees through n@f6 to the valuable q@e7 behind it.",
          "evidence": "B@g5 sees through n@f6 to the valuable q@e7 behind it",
          "source": {
            "theme": "x_ray",
            "squares": [
              "g5",
              "f6",
              "e7"
            ],
            "pieces": [
              "B@g5"
            ],
            "confidence": 0.6
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Weakens opponent king: opponent king safety drops from -3.00 to -4.00.",
          "evidence": "opponent king safety drops from -3.00 to -4.00",
          "source": {
            "theme": "weakens_opponent_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Passed pawn: passed pawn on c2.",
          "evidence": "passed pawn on c2",
          "source": {
            "theme": "passed_pawn",
            "squares": [
              "c2"
            ],
            "pieces": [
              "P@c2"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Rook open file: rook on the open d-file.",
          "evidence": "rook on the open d-file",
          "source": {
            "theme": "rook_open_file",
            "squares": [
              "d1"
            ],
            "pieces": [
              "R@d1"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bishop pair: the mover owns both bishops.",
          "evidence": "the mover owns both bishops",
          "source": {
            "theme": "bishop_pair",
            "squares": [
              "b5",
              "g5"
            ],
            "pieces": [
              "B@b5",
              "B@g5"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Controls center: central control rises from 1.00 to 2.00.",
          "evidence": "central control rises from 1.00 to 2.00",
          "source": {
            "theme": "controls_center",
            "squares": [],
            "pieces": [],
            "confidence": 0.8
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Mobility: improved by 36.0.",
          "evidence": "positional_delta.mobility=36.0",
          "source": {
            "group": "mobility",
            "value": 36.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Space: improved by 4.0.",
          "evidence": "positional_delta.space=4.0",
          "source": {
            "group": "space",
            "value": 4.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Activity: improved by 5.0.",
          "evidence": "positional_delta.activity=5.0",
          "source": {
            "group": "activity",
            "value": 5.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 attacks king: pressure on the enemy king rises.",
          "evidence": "pressure on the enemy king rises",
          "source": {
            "tag": "attacks_king",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 27,
      "move_san": "Qe6",
      "move_uci": "e7e6",
      "headline": "Qe6 \u2014 an excellent move.",
      "sentences": [
        "The evaluation remains -8.11 for the mover.",
        "Skewer: q@e6 skewers the valuable Q@b3, which must step aside and let P@a2 fall.",
        "Threat created: the move now attacks the defended Q@b3.",
        "Interference: q@e6 interposes on the Q@b3's line, denying the capture on f7.",
        "Shelters king: king safety rises from -4.00 to -3.00.",
        "Weakens opponent king: opponent king safety drops from -1.00 to -2.00.",
        "Isolated pawn: isolated pawn on a7.",
        "Mobility: improved by 66.0.",
        "King safety: improved by 12.0.",
        "Intent \u2014 improves piece: the q moves toward the centre.",
        "Intent \u2014 restricts opponent: opponent mobility drops from 37.0 to 36.0.",
        "Intent \u2014 attacks king: pressure on the enemy king rises."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "Qe6 \u2014 an excellent move.",
          "evidence": "quality.label=excellent",
          "source": {
            "move_san": "Qe6",
            "label": "excellent"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "The evaluation remains -8.11 for the mover.",
          "evidence": "eval_before_cp=-716.0, eval_after_cp=-811.0, loss_cp=95.0, loss_wp=0.019",
          "source": {
            "label": "excellent",
            "eval_after_cp": -811.0,
            "loss_cp": 95.0,
            "loss_wp": 0.018779383739714862
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Skewer: q@e6 skewers the valuable Q@b3, which must step aside and let P@a2 fall.",
          "evidence": "q@e6 skewers the valuable Q@b3, which must step aside and let P@a2 fall",
          "source": {
            "theme": "skewer",
            "squares": [
              "e6",
              "b3",
              "a2"
            ],
            "pieces": [
              "q@e6"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Threat created: the move now attacks the defended Q@b3.",
          "evidence": "the move now attacks the defended Q@b3",
          "source": {
            "theme": "threat_created",
            "squares": [
              "b3"
            ],
            "pieces": [
              "Q@b3",
              "q@e6"
            ],
            "confidence": 0.8
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Interference: q@e6 interposes on the Q@b3's line, denying the capture on f7.",
          "evidence": "q@e6 interposes on the Q@b3's line, denying the capture on f7",
          "source": {
            "theme": "interference",
            "squares": [
              "b3",
              "e6",
              "f7"
            ],
            "pieces": [
              "Q@b3",
              "q@e6"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Shelters king: king safety rises from -4.00 to -3.00.",
          "evidence": "king safety rises from -4.00 to -3.00",
          "source": {
            "theme": "shelters_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Weakens opponent king: opponent king safety drops from -1.00 to -2.00.",
          "evidence": "opponent king safety drops from -1.00 to -2.00",
          "source": {
            "theme": "weakens_opponent_king",
            "squares": [
              "c1"
            ],
            "pieces": [
              "K@c1"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Isolated pawn: isolated pawn on a7.",
          "evidence": "isolated pawn on a7",
          "source": {
            "theme": "isolated_pawn",
            "squares": [
              "a7"
            ],
            "pieces": [
              "p@a7"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Mobility: improved by 66.0.",
          "evidence": "positional_delta.mobility=66.0",
          "source": {
            "group": "mobility",
            "value": 66.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "King safety: improved by 12.0.",
          "evidence": "positional_delta.king_safety=12.0",
          "source": {
            "group": "king_safety",
            "value": 12.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 improves piece: the q moves toward the centre.",
          "evidence": "the q moves toward the centre",
          "source": {
            "tag": "improves_piece",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 restricts opponent: opponent mobility drops from 37.0 to 36.0.",
          "evidence": "opponent mobility drops from 37.0 to 36.0",
          "source": {
            "tag": "restricts_opponent",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 attacks king: pressure on the enemy king rises.",
          "evidence": "pressure on the enemy king rises",
          "source": {
            "tag": "attacks_king",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 28,
      "move_san": "Bxd7+",
      "move_uci": "b5d7",
      "headline": "Bxd7+ \u2014 the best move.",
      "sentences": [
        "The evaluation remains +9.99 for the mover.",
        "The move is forcing: a check or a forced mate.",
        "Fork: B@d7 hits q@e6 and k@e8 at once and does not hang.",
        "Skewer: Q@b3 skewers the valuable q@e6, which must step aside and let p@f7 fall.",
        "Hanging piece: q@e6 is left hanging (1 attackers against its defenders).",
        "Trapped piece: q@e6 is attacked and every square it can reach is covered too.",
        "Capture: takes the r@d7.",
        "Shelters king: king safety rises from -2.00 to 1.00.",
        "Weakens opponent king: opponent king safety drops from -3.00 to -4.00.",
        "Passed pawn: passed pawn on c2.",
        "Bishop pair: the mover owns both bishops.",
        "Material: the mover gained 5.00 pawns.",
        "Mobility: improved by 6.0.",
        "King safety: improved by 36.0.",
        "Activity: improved by 5.0.",
        "Intent \u2014 restricts opponent: opponent mobility drops from 32.0 to 24.0.",
        "Intent \u2014 attacks king: Bxd7+ gives check."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "Bxd7+ \u2014 the best move.",
          "evidence": "quality.label=best",
          "source": {
            "move_san": "Bxd7+",
            "label": "best"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "The evaluation remains +9.99 for the mover.",
          "evidence": "eval_before_cp=999.0, eval_after_cp=999.0, loss_cp=0.0, loss_wp=0.000",
          "source": {
            "label": "best",
            "eval_after_cp": 999.0,
            "loss_cp": 0.0,
            "loss_wp": 0.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "The move is forcing: a check or a forced mate.",
          "evidence": "is_forcing=True",
          "source": {
            "flag": "is_forcing",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Fork: B@d7 hits q@e6 and k@e8 at once and does not hang.",
          "evidence": "B@d7 hits q@e6 and k@e8 at once and does not hang",
          "source": {
            "theme": "fork",
            "squares": [
              "d7",
              "e6",
              "e8"
            ],
            "pieces": [
              "B@d7"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Skewer: Q@b3 skewers the valuable q@e6, which must step aside and let p@f7 fall.",
          "evidence": "Q@b3 skewers the valuable q@e6, which must step aside and let p@f7 fall",
          "source": {
            "theme": "skewer",
            "squares": [
              "b3",
              "e6",
              "f7"
            ],
            "pieces": [
              "Q@b3"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Hanging piece: q@e6 is left hanging (1 attackers against its defenders).",
          "evidence": "q@e6 is left hanging (1 attackers against its defenders)",
          "source": {
            "theme": "hanging_piece",
            "squares": [
              "e6"
            ],
            "pieces": [
              "q@e6"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Trapped piece: q@e6 is attacked and every square it can reach is covered too.",
          "evidence": "q@e6 is attacked and every square it can reach is covered too",
          "source": {
            "theme": "trapped_piece",
            "squares": [
              "e6"
            ],
            "pieces": [
              "q@e6"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Capture: takes the r@d7.",
          "evidence": "takes the r@d7",
          "source": {
            "theme": "capture",
            "squares": [
              "b5",
              "d7"
            ],
            "pieces": [
              "B@d7"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Shelters king: king safety rises from -2.00 to 1.00.",
          "evidence": "king safety rises from -2.00 to 1.00",
          "source": {
            "theme": "shelters_king",
            "squares": [
              "c1"
            ],
            "pieces": [
              "K@c1"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Weakens opponent king: opponent king safety drops from -3.00 to -4.00.",
          "evidence": "opponent king safety drops from -3.00 to -4.00",
          "source": {
            "theme": "weakens_opponent_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Passed pawn: passed pawn on c2.",
          "evidence": "passed pawn on c2",
          "source": {
            "theme": "passed_pawn",
            "squares": [
              "c2"
            ],
            "pieces": [
              "P@c2"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Bishop pair: the mover owns both bishops.",
          "evidence": "the mover owns both bishops",
          "source": {
            "theme": "bishop_pair",
            "squares": [
              "g5",
              "d7"
            ],
            "pieces": [
              "B@g5",
              "B@d7"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Material: the mover gained 5.00 pawns.",
          "evidence": "positional_delta.material=500.0",
          "source": {
            "group": "material",
            "value": 500.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Mobility: improved by 6.0.",
          "evidence": "positional_delta.mobility=6.0",
          "source": {
            "group": "mobility",
            "value": 6.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "King safety: improved by 36.0.",
          "evidence": "positional_delta.king_safety=36.0",
          "source": {
            "group": "king_safety",
            "value": 36.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Activity: improved by 5.0.",
          "evidence": "positional_delta.activity=5.0",
          "source": {
            "group": "activity",
            "value": 5.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 restricts opponent: opponent mobility drops from 32.0 to 24.0.",
          "evidence": "opponent mobility drops from 32.0 to 24.0",
          "source": {
            "tag": "restricts_opponent",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 attacks king: Bxd7+ gives check.",
          "evidence": "Bxd7+ gives check",
          "source": {
            "tag": "attacks_king",
            "moves": [],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 29,
      "move_san": "Nxd7",
      "move_uci": "f6d7",
      "headline": "Nxd7 \u2014 a great move.",
      "sentences": [
        "The evaluation remains -3.15 for the mover.",
        "It was the only move that keeps the position.",
        "The move is forcing: a check or a forced mate.",
        "The position was critical: small differences in the evaluation mattered.",
        "Skewer: q@e6 skewers the valuable Q@b3, which must step aside and let P@a2 fall.",
        "Hanging piece defended: q@e6 was hanging and is now covered by n@d7.",
        "Capture: takes the B@d7.",
        "Exposes king: king safety drops from -4.00 to -5.00.",
        "Isolated pawn: isolated pawn on a7.",
        "Material: the mover gained 3.30 pawns.",
        "King safety: worsened by 12.0.",
        "Space: worsened by 4.0.",
        "Activity: worsened by 5.0.",
        "Intent \u2014 restricts opponent: opponent mobility drops from 37.0 to 34.0.",
        "Intent \u2014 defends material: the move covers an attacked piece."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "Nxd7 \u2014 a great move.",
          "evidence": "quality.label=great",
          "source": {
            "move_san": "Nxd7",
            "label": "great"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "The evaluation remains -3.15 for the mover.",
          "evidence": "eval_before_cp=-315.0, eval_after_cp=-315.0, loss_cp=0.0, loss_wp=0.000",
          "source": {
            "label": "great",
            "eval_after_cp": -315.0,
            "loss_cp": 0.0,
            "loss_wp": 0.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "It was the only move that keeps the position.",
          "evidence": "is_only_move=True, gap_to_second_wp=0.213",
          "source": {
            "flag": "is_only_move",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "The move is forcing: a check or a forced mate.",
          "evidence": "is_forcing=True",
          "source": {
            "flag": "is_forcing",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "The position was critical: small differences in the evaluation mattered.",
          "evidence": "is_critical=True, sharpness=0.235",
          "source": {
            "flag": "is_critical",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Skewer: q@e6 skewers the valuable Q@b3, which must step aside and let P@a2 fall.",
          "evidence": "q@e6 skewers the valuable Q@b3, which must step aside and let P@a2 fall",
          "source": {
            "theme": "skewer",
            "squares": [
              "e6",
              "b3",
              "a2"
            ],
            "pieces": [
              "q@e6"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Hanging piece defended: q@e6 was hanging and is now covered by n@d7.",
          "evidence": "q@e6 was hanging and is now covered by n@d7",
          "source": {
            "theme": "hanging_piece_defended",
            "squares": [
              "e6",
              "d7"
            ],
            "pieces": [
              "q@e6",
              "n@d7"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Capture: takes the B@d7.",
          "evidence": "takes the B@d7",
          "source": {
            "theme": "capture",
            "squares": [
              "f6",
              "d7"
            ],
            "pieces": [
              "n@d7"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Exposes king: king safety drops from -4.00 to -5.00.",
          "evidence": "king safety drops from -4.00 to -5.00",
          "source": {
            "theme": "exposes_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Isolated pawn: isolated pawn on a7.",
          "evidence": "isolated pawn on a7",
          "source": {
            "theme": "isolated_pawn",
            "squares": [
              "a7"
            ],
            "pieces": [
              "p@a7"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Material: the mover gained 3.30 pawns.",
          "evidence": "positional_delta.material=330.0",
          "source": {
            "group": "material",
            "value": 330.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "King safety: worsened by 12.0.",
          "evidence": "positional_delta.king_safety=-12.0",
          "source": {
            "group": "king_safety",
            "value": -12.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Space: worsened by 4.0.",
          "evidence": "positional_delta.space=-4.0",
          "source": {
            "group": "space",
            "value": -4.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Activity: worsened by 5.0.",
          "evidence": "positional_delta.activity=-5.0",
          "source": {
            "group": "activity",
            "value": -5.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 restricts opponent: opponent mobility drops from 37.0 to 34.0.",
          "evidence": "opponent mobility drops from 37.0 to 34.0",
          "source": {
            "tag": "restricts_opponent",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 defends material: the move covers an attacked piece.",
          "evidence": "the move covers an attacked piece",
          "source": {
            "tag": "defends_material",
            "moves": [],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 30,
      "move_san": "Qb8+",
      "move_uci": "b3b8",
      "headline": "Qb8+ \u2014 a great move.",
      "sentences": [
        "The evaluation remains winning by force.",
        "It was the only move that keeps the position.",
        "The move is forcing: a check or a forced mate.",
        "The position was critical: small differences in the evaluation mattered.",
        "X ray: Q@b8 sees through k@e8 to the valuable b@f8 behind it.",
        "Passed pawn: passed pawn on c2.",
        "Controls center: central control rises from 2.00 to 3.00.",
        "Intent \u2014 attacks king: Qb8+ gives check."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "Qb8+ \u2014 a great move.",
          "evidence": "quality.label=great",
          "source": {
            "move_san": "Qb8+",
            "label": "great"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "The evaluation remains winning by force.",
          "evidence": "eval_before_cp=9998.0, eval_after_cp=9998.0, loss_cp=0.0, loss_wp=0.000",
          "source": {
            "label": "great",
            "eval_after_cp": 9998.0,
            "loss_cp": 0.0,
            "loss_wp": 0.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "It was the only move that keeps the position.",
          "evidence": "is_only_move=True, gap_to_second_wp=0.212",
          "source": {
            "flag": "is_only_move",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "The move is forcing: a check or a forced mate.",
          "evidence": "is_forcing=True",
          "source": {
            "flag": "is_forcing",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "The position was critical: small differences in the evaluation mattered.",
          "evidence": "is_critical=True, sharpness=0.234",
          "source": {
            "flag": "is_critical",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "X ray: Q@b8 sees through k@e8 to the valuable b@f8 behind it.",
          "evidence": "Q@b8 sees through k@e8 to the valuable b@f8 behind it",
          "source": {
            "theme": "x_ray",
            "squares": [
              "b8",
              "e8",
              "f8"
            ],
            "pieces": [
              "Q@b8"
            ],
            "confidence": 0.6
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Passed pawn: passed pawn on c2.",
          "evidence": "passed pawn on c2",
          "source": {
            "theme": "passed_pawn",
            "squares": [
              "c2"
            ],
            "pieces": [
              "P@c2"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Controls center: central control rises from 2.00 to 3.00.",
          "evidence": "central control rises from 2.00 to 3.00",
          "source": {
            "theme": "controls_center",
            "squares": [],
            "pieces": [],
            "confidence": 0.8
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 attacks king: Qb8+ gives check.",
          "evidence": "Qb8+ gives check",
          "source": {
            "tag": "attacks_king",
            "moves": [],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 31,
      "move_san": "Nxb8",
      "move_uci": "d7b8",
      "headline": "Nxb8 \u2014 the best move.",
      "sentences": [
        "The evaluation remains losing by force.",
        "The move is forcing: a check or a forced mate.",
        "Capture: takes the Q@b8.",
        "Shelters king: king safety rises from -5.00 to -4.00.",
        "Isolated pawn: isolated pawn on a7.",
        "Material: the mover gained 9.00 pawns.",
        "Mobility: improved by 6.0.",
        "King safety: improved by 12.0.",
        "Activity: worsened by 5.0.",
        "Intent \u2014 restricts opponent: opponent mobility drops from 31.0 to 19.0."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "Nxb8 \u2014 the best move.",
          "evidence": "quality.label=best",
          "source": {
            "move_san": "Nxb8",
            "label": "best"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "The evaluation remains losing by force.",
          "evidence": "eval_before_cp=-9999.0, eval_after_cp=-9999.0, loss_cp=0.0, loss_wp=0.000",
          "source": {
            "label": "best",
            "eval_after_cp": -9999.0,
            "loss_cp": 0.0,
            "loss_wp": 0.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "The move is forcing: a check or a forced mate.",
          "evidence": "is_forcing=True",
          "source": {
            "flag": "is_forcing",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Capture: takes the Q@b8.",
          "evidence": "takes the Q@b8",
          "source": {
            "theme": "capture",
            "squares": [
              "d7",
              "b8"
            ],
            "pieces": [
              "n@b8"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Shelters king: king safety rises from -5.00 to -4.00.",
          "evidence": "king safety rises from -5.00 to -4.00",
          "source": {
            "theme": "shelters_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Isolated pawn: isolated pawn on a7.",
          "evidence": "isolated pawn on a7",
          "source": {
            "theme": "isolated_pawn",
            "squares": [
              "a7"
            ],
            "pieces": [
              "p@a7"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Material: the mover gained 9.00 pawns.",
          "evidence": "positional_delta.material=900.0",
          "source": {
            "group": "material",
            "value": 900.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Mobility: improved by 6.0.",
          "evidence": "positional_delta.mobility=6.0",
          "source": {
            "group": "mobility",
            "value": 6.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "King safety: improved by 12.0.",
          "evidence": "positional_delta.king_safety=12.0",
          "source": {
            "group": "king_safety",
            "value": 12.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "positional",
          "text": "Activity: worsened by 5.0.",
          "evidence": "positional_delta.activity=-5.0",
          "source": {
            "group": "activity",
            "value": -5.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 restricts opponent: opponent mobility drops from 31.0 to 19.0.",
          "evidence": "opponent mobility drops from 31.0 to 19.0",
          "source": {
            "tag": "restricts_opponent",
            "moves": [],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    },
    {
      "ply": 32,
      "move_san": "Rd8#",
      "move_uci": "d1d8",
      "headline": "Rd8# \u2014 a great move.",
      "sentences": [
        "The evaluation remains winning by force.",
        "It was the only move that keeps the position.",
        "The move is forcing: a check or a forced mate.",
        "The position was critical: small differences in the evaluation mattered.",
        "Fork: R@d8 hits n@b8 and k@e8 at once and does not hang.",
        "Hanging piece: n@b8 is left hanging (1 attackers against its defenders).",
        "Back rank mate: Rd8# mates: the king on e8 never left its back rank.",
        "X ray: R@d8 sees through k@e8 to the valuable b@f8 behind it.",
        "Weakens opponent king: opponent king safety drops from -4.00 to -5.00.",
        "Passed pawn: passed pawn on c2.",
        "Rook open file: rook on the open d-file.",
        "Develops piece: R@d8 develops off the back rank.",
        "Intent \u2014 develops: develops the R to d8.",
        "Intent \u2014 attacks king: Rd8# gives check."
      ],
      "claims": [
        {
          "kind": "headline",
          "text": "Rd8# \u2014 a great move.",
          "evidence": "quality.label=great",
          "source": {
            "move_san": "Rd8#",
            "label": "great"
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "evaluation",
          "text": "The evaluation remains winning by force.",
          "evidence": "eval_before_cp=9999.0, eval_after_cp=9999.0, loss_cp=0.0, loss_wp=0.000",
          "source": {
            "label": "great",
            "eval_after_cp": 9999.0,
            "loss_cp": 0.0,
            "loss_wp": 0.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "It was the only move that keeps the position.",
          "evidence": "is_only_move=True, gap_to_second_wp=0.956",
          "source": {
            "flag": "is_only_move",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "The move is forcing: a check or a forced mate.",
          "evidence": "is_forcing=True",
          "source": {
            "flag": "is_forcing",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "criticality",
          "text": "The position was critical: small differences in the evaluation mattered.",
          "evidence": "is_critical=True, sharpness=0.957",
          "source": {
            "flag": "is_critical",
            "value": true
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Fork: R@d8 hits n@b8 and k@e8 at once and does not hang.",
          "evidence": "R@d8 hits n@b8 and k@e8 at once and does not hang",
          "source": {
            "theme": "fork",
            "squares": [
              "d8",
              "b8",
              "e8"
            ],
            "pieces": [
              "R@d8"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Hanging piece: n@b8 is left hanging (1 attackers against its defenders).",
          "evidence": "n@b8 is left hanging (1 attackers against its defenders)",
          "source": {
            "theme": "hanging_piece",
            "squares": [
              "b8"
            ],
            "pieces": [
              "n@b8"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Back rank mate: Rd8# mates: the king on e8 never left its back rank.",
          "evidence": "Rd8# mates: the king on e8 never left its back rank",
          "source": {
            "theme": "back_rank_mate",
            "squares": [
              "d8",
              "e8"
            ],
            "pieces": [
              "R@d8"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "X ray: R@d8 sees through k@e8 to the valuable b@f8 behind it.",
          "evidence": "R@d8 sees through k@e8 to the valuable b@f8 behind it",
          "source": {
            "theme": "x_ray",
            "squares": [
              "d8",
              "e8",
              "f8"
            ],
            "pieces": [
              "R@d8"
            ],
            "confidence": 0.6
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Weakens opponent king: opponent king safety drops from -4.00 to -5.00.",
          "evidence": "opponent king safety drops from -4.00 to -5.00",
          "source": {
            "theme": "weakens_opponent_king",
            "squares": [
              "e8"
            ],
            "pieces": [
              "k@e8"
            ],
            "confidence": 0.7
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Passed pawn: passed pawn on c2.",
          "evidence": "passed pawn on c2",
          "source": {
            "theme": "passed_pawn",
            "squares": [
              "c2"
            ],
            "pieces": [
              "P@c2"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Rook open file: rook on the open d-file.",
          "evidence": "rook on the open d-file",
          "source": {
            "theme": "rook_open_file",
            "squares": [
              "d8"
            ],
            "pieces": [
              "R@d8"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "theme",
          "text": "Develops piece: R@d8 develops off the back rank.",
          "evidence": "R@d8 develops off the back rank",
          "source": {
            "theme": "develops_piece",
            "squares": [
              "d1",
              "d8"
            ],
            "pieces": [
              "R@d8"
            ],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 develops: develops the R to d8.",
          "evidence": "develops the R to d8",
          "source": {
            "tag": "develops",
            "moves": [],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        },
        {
          "kind": "intent",
          "text": "Intent \u2014 attacks king: Rd8# gives check.",
          "evidence": "Rd8# gives check",
          "source": {
            "tag": "attacks_king",
            "moves": [],
            "confidence": 1.0
          },
          "confidence": 1.0,
          "verified": true
        }
      ],
      "unverified": [],
      "verified": true
    }
  ]
}
